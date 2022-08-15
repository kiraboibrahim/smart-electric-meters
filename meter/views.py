import uuid
import time
import math
import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponse, Http404
from django.views.generic import list as generic_list_views
from django.views.generic import edit as generic_edit_views
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.conf import settings
from django.views import View

from prepaid_meters_token_generator_system import user_permission_tests
from prepaid_meters_token_generator_system.utils.mixins import user_permissions as user_permission_mixins
from prepaid_meters_token_generator_system.utils import views as custom_generic_views

from meter import utils as meter_utils
from meter import models as meter_models
from meter.externalAPI.meters import MeterAPIFactoryImpl, MeterAPIException
from meter.externalAPI import DTOs as DTO
from meter import forms as meter_forms

from user import models as user_models


User = get_user_model()


def get_meter_charges(meter):
    percentage_charge = meter.category.percentage_charge/100
    fixed_charge = meter.category.fixed_charge
    return (percentage_charge, fixed_charge)


def get_net_amount(gross_amount, charges):
    percentage_charge = charges[0]
    fixed_charge = charges[1]
    total_charge = percentage_charge*gross_amount + fixed_charge
    net_amount = gross_amount - total_charge
    return net_amount
    

def get_token(token_spec):
    meter = token_spec.meter
    gross_amount = token_spec.amount
    charges = get_meter_charges(meter)
    net_amount = get_net_amount(gross_amount, charges)
    token_spec.amount = net_amount # Get token worth the net amount and not the gross amount
    unit_price = meter.manager.unit_price.price
    num_of_token_units = math.ceil(net_amount / unit_price)
    
    API_id = meter_utils.get_meter_manufacturer_hash(meter.manufacturer.name)
    meter_API = MeterAPIFactoryImpl.get_API(API_id)
    token = meter_API.get_token(token_spec)
    return token

    
def log_token(token):
    token_log = meter_models.TokenLog()
    token_log.user = token.buyer
    token_log.token_no = token.number
    token_log.amount = token.amount
    token_log.num_of_units = token.num_of_units
    token_log.meter = token.meter
    
    token_log.save()
    return token_log


def register_meter_customer(customer, meter):
    customer = DTO.MeterCustomer(customer)
    customer.set_meter(meter)
    API_id = meter_utils.get_meter_manufacturer_hash(meter.manufacturer.name)
    meter_API = MeterAPIFactoryImpl.get_API(API_id)
    return meter_API.register_customer(customer)


class MeterManufacturerListView(user_permission_mixins.AdminOrSuperAdminRequiredMixin, generic_list_views.ListView):
    template_name = "meter/list_manufacturers.html.development"
    context_object_name = "manufacturers"
    model = meter_models.Manufacturer

    def get_context_data(self, **kwargs):
        context = super(MeterManufacturerListView, self).get_context_data(**kwargs)

        add_meter_manufacturer_form = meter_forms.AddMeterManufacturerForm()
        
        context["add_meter_manufacturer_form"] = add_meter_manufacturer_form
        
        return context

    
class MeterManufacturerCreateView(user_permission_mixins.AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, generic_edit_views.CreateView):
    form_class = meter_forms.AddMeterManufacturerForm
    template_name = "meter/list_manufacturers.html.development"
    success_url = reverse_lazy("list_meter_manufacturers")
    success_message = "Meter: %(manufacturer)s added successfully ."
    
    def get_success_message(self, cleaned_data):
        # Make the meter number accessible in the success_message
        return self.success_message % dict(
            cleaned_data,
            manufacturer=self.object.name,
        )
    

class MeterManufacturerEditView(user_permission_mixins.AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, generic_edit_views.UpdateView):
    model = meter_models.Manufacturer
    fields = "__all__"
    template_name = "meter/edit_manufacturer.html.development"
    extra_context = {"manufacturers": meter_models.Manufacturer.objects.all()}
    success_message = "Changes saved successfully."

    def get_success_url(self):
        url = reverse_lazy("list_meter_manufacturers")
        return url

    def get_context_data(self, **kwargs):
        context = super(MeterManufacturerEditView, self).get_context_data(**kwargs)
        
        context["edit_meter_manufacturer_form"] = context["form"]
        
        return context

    

class MeterCreateView(user_permission_mixins.AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, generic_edit_views.CreateView):
    form_class = meter_forms.AddMeterForm
    template_name = "meter/list_meters.html.development"
    success_message = "Meter: %(meter_no)s registered successfully."
    success_url = reverse_lazy("list_meters")
    http_method_names = ["post"]
    
    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            meter_no=self.object.meter_no,
        )

    def get_context_data(self, **kwargs):
        base_context = super(MeterCreateView, self).get_context_data(**kwargs)
        context = meter_utils.get_list_meters_template_context_data(self.request, base_context)

        return context
    
    def form_valid(self, form):
        is_meter_remotely_registered = form.cleaned_data.pop("is_registered") # Iam using pop() method to remove it from the fields
        meter = meter_models.Meter(**form.cleaned_data)
        meter_customer = meter.manager
        
  
        try:
            if not is_meter_remotely_registered:
                register_meter_customer(meter_customer, meter)
        except MeterAPIException:
            messages.error(self.request, "Registration with the meter manufacturer has failed")
            return super(MeterCreateView, self).form_invalid(form)
        
        return super(MeterCreateView, self).form_valid(form)

    
class MeterEditView(user_permission_mixins.AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, generic_edit_views.UpdateView):
    model = meter_models.Meter
    fields = "__all__"
    template_name = "meter/edit_meter.html.development"
    success_message = "Changes saved successfully."

    def get_success_url(self):
        url = reverse_lazy("edit_meter", kwargs={"pk":self.object.id})
        return url

    
    
class MeterListView(LoginRequiredMixin, custom_generic_views.FiltersListView):
    template_name = "meter/list_meters.html.development"
    context_object_name = "meters"
    model = meter_models.Meter
    paginate_by = settings.MAX_ITEMS_PER_PAGE
    
    filters_form_class = meter_forms.Filters
        
    def get_context_data(self, **kwargs):
        base_context = super(MeterListView, self).get_context_data(**kwargs)
        return meter_utils.get_list_meters_template_context_data(self.request, base_context) 
    
    
class MeterSearchView(custom_generic_views.SearchListView):
    template_name = "meter/list_meters.html.development"
    model = meter_models.Meter
    context_object_name = "meters"
    http_method_names = ["get"]
    paginate_by = settings.MAX_ITEMS_PER_PAGE
    filters_form_class = meter_forms.Filters
    search_form_class = meter_forms.SearchForm

    def get_context_data(self, **kwargs):
        base_context = super(MeterSearchView, self).get_context_data(**kwargs)
        context = meter_utils.get_list_meters_template_context_data(self.request, base_context)
        return context
    

    
class MeterEditView(user_permission_mixins.AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, generic_edit_views.UpdateView):
    model = meter_models.Meter
    fields = "__all__"
    template_name = "meter/edit_meter.html.development"
    success_message = "Changes saved successfully."

    def get_success_url(self):
        url = reverse_lazy("edit_meter", kwargs={"pk":self.object.id})
        return url

    def get_context_data(self, **kwwargs):
        context = super(MeterEditView, self).get_context_data(**kwargs)
        context["meters"] = meter_utils.get_meters(self.request)
    
    
class MeterCategoryCreateView(user_permission_mixins.AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, generic_edit_views.CreateView):
    model = meter_models.MeterCategory
    template_name = "meter/list_meters.html.development"
    fields = "__all__"
    success_url = reverse_lazy("list_meters")
    success_message = "Meter category: %(label)s added successfully"
    
    def get_success_message(self, cleaned_data):
        # Make meter fields accessible to the success_message 
        return self.success_message % dict(cleaned_data)

    def get_context_data(self, **kwargs):
        context = super(MeterCategoryCreateView, self).get_context_data(**kwargs)
        
        add_meter_form = meter_forms.AddMeterForm()
        context["add_meter_category_form"] = context["form"]
        context["add_meter_form"] = add_meter_form
        
        context["meters"] = meter_utils.get_meters(self.request)

        return context

    

class RechargeMeterView(View):

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        form = self.get_recharge_meter_form(pk)
        context = {
            "form": form,
            "meters": meter_utils.get_meters(request)
        }
        return render(request, "meter/recharge_meter.html.development", context)

    def get_recharge_meter_form(self, pk):
        recharge_meter_form = None
        if pk:
            meter = get_object_or_404(meter_models.Meter, pk=pk)
            recharge_meter_form = meter_forms.RechargeMeterForm(initial={"meter_no": meter.meter_no})
        else:
            recharge_meter_form = meter_forms.RechargeMeterForm()

        return recharge_meter_form
    
    def post(self, request, *args, **kwargs):
        recharge_meter_form = meter_forms.RechargeMeterForm(request.POST)
        buyer = request.user
        if recharge_meter_form.is_valid():
            gross_amount = recharge_meter_form.cleaned_data.get("amount")
            
            token_spec = DTO.TokenSpec()
            token_spec.meter = recharge_meter_form.meter
            token_spec.buyer = buyer
            token_spec.amount = gross_amount

            try:
                token = get_token(token_spec)
            except MeterAPIException:
                messages.error(request, "Token purchase has failed")
            else:
                log_token(token)
                    
                """ TODO: Send SMS to user with token number """
                messages.success(request, "Token: %s Units: %s KWH" %(token.number, token.num_of_units))

        context = {
            "form": recharge_meter_form,
            "meters": meter_utils.get_meters(request),
        }
        return render(request, "meter/recharge_meter.html.development", context)
        


@user_passes_test(user_permission_tests.is_admin_or_super_admin)
def deactivate_meter(request, pk):
    meter = get_object_or_404(meter_models.Meter, pk=pk)
    meter.is_active = False
    meter.save()
    
    messages.success(request, "Meter: %s has been deleted successfully" %(meter.meter_no))
    return redirect("list_meters")
