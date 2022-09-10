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
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView, FormMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.conf import settings
from django.views import View

from search_views.filters import build_q

from prepaid_meters_token_generator_system.utils.mixins.user_permissions import AdminOrSuperAdminRequiredMixin
from prepaid_meters_token_generator_system.user_permission_tests import is_admin_or_super_admin

from meter.utils import get_meter_queryset, get_list_meters_template_context_data 
from meter.forms import AddMeterForm, SearchMeterForm, RechargeMeterForm
from meter.models import Meter
from meter.filters import MeterSearchFilter
import meter.externalAPI.DTOs as DTO
from meter.externalAPI.meters import MeterAPIFactoryImpl, MeterAPIException


User = get_user_model()

class MeterCreateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = AddMeterForm
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
        context = get_list_meters_template_context_data(self.request, base_context)

        return context
    
    def form_valid(self, form):
        is_meter_remotely_registered = form.cleaned_data.pop("is_registered") # Iam using pop() method to remove it from the fields
        meter = Meter(**form.cleaned_data)
        meter_customer = meter.manager
        
  
        try:
            if not is_meter_remotely_registered:
                register_meter_customer(meter_customer, meter)
        except MeterAPIException:
            messages.error(self.request, "Registration with the meter manufacturer has failed")
            return super(MeterCreateView, self).form_invalid(form)
        
        return super(MeterCreateView, self).form_valid(form)

    
    
class MeterListView(LoginRequiredMixin, ListView):
    template_name = "meter/list_meters.html.development"
    context_object_name = "meters"
    model = Meter
        
    def get_context_data(self, **kwargs):
        base_context = super(MeterListView, self).get_context_data(**kwargs)
        return get_list_meters_template_context_data(self.request, base_context) 
    
    
class MeterSearchView(ListView, FormMixin):
    model = Meter
    template_name = "meter/search_meters.html.development"
    context_object_name = "meters"
    http_method_names = ["get"]
    form_class = SearchMeterForm
    filters_class = MeterSearchFilter

    def get_queryset(self):
        search_query = build_q(self.filters_class.get_search_fields(), self.request.GET)
        qs = get_meter_queryset(self.request.user).filter(search_query)
        return qs
        
    def get_context_data(self, **kwargs):
        base_context = super(MeterSearchView, self).get_context_data(**kwargs)
        context = get_list_meters_template_context_data(self.request, base_context)
        return context

    
class MeterEditView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Meter
    fields = "__all__"
    template_name = "meter/edit_meter.html.development"
    success_message = "Changes saved successfully."

    def get_success_url(self):
        return reverse_lazy("edit_meter", kwargs={"pk":self.object.id})

    def get_context_data(self, **kwargs):
        context = super(MeterEditView, self).get_context_data(**kwargs)
        context["meters"] = get_meter_queryset(self.request)
        return context
    

class RechargeMeterView(View):

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        form = self.get_recharge_meter_form(pk)
        context = {
            "form": form,
            "meters": get_meter_queryset(request.user)
        }
        return render(request, "meter/recharge_meter.html.development", context)

    def get_recharge_meter_form(self, pk):
        recharge_meter_form = None
        if pk:
            meter = get_object_or_404(Meter, pk=pk)
            recharge_meter_form = RechargeMeterForm(initial={"meter_no": meter.meter_no})
        else:
            recharge_meter_form = RechargeMeterForm()

        return recharge_meter_form
    
    def post(self, request, *args, **kwargs):
        recharge_meter_form = RechargeMeterForm(request.POST)
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
            "meters": get_meter_queryset(request.user),
        }
        return render(request, "meter/recharge_meter.html.development", context)
        


@user_passes_test(is_admin_or_super_admin)
def deactivate_meter(request, pk):
    meter = get_object_or_404(meter_models.Meter, pk=pk)
    meter.is_active = False
    meter.save()
    
    messages.success(request, "Meter: %s has been deleted successfully" %(meter.meter_no))
    return redirect("list_meters")
