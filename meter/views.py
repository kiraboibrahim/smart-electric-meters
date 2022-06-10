import uuid
import time
import math
import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponse, Http404
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.conf import settings
from django.views import View

from meter.utils import is_admin, is_super_admin, is_admin_or_super_admin, SuperAdminRequiredMixin, AdminRequiredMixin, AdminOrSuperAdminRequiredMixin, create_meter_manufacturer_hash
from meter.models import MeterCategory, Meter, Manufacturer, TokenLog
from meter.api import MeterAPIFactoryImpl, MeterAPIException
from meter.forms import BuyTokenForm
from meter import payloads

from transaction.models import Transaction

from user.acc_types import MANAGER
from user.models import PricePerUnit

# Create your views here.
User = get_user_model()

def get_charges_ugx(meter, gross_amount_ugx):
    percentage_charge = meter.meter_category.percentage_charge
    fixed_charge_ugx = meter.meter_category.fixed_charge
    total_charges_ugx = math.ceil(((percentage_charge / 100) * gross_amount_ugx) + fixed_charge_ugx)
    return total_charges_ugx

def get_net_amount_ugx(meter, gross_amount_ugx):
    total_charges_ugx = get_charges_ugx(meter, gross_amount_ugx)
    net_amount_ugx = gross_amount_ugx - total_charges_ugx
    return net_amount_ugx
    
def get_token(meter, gross_amount_ugx):
    net_amount_ugx = get_net_amount_ugx(meter, gross_amount_ugx)
    num_token_units = math.ceil(net_amount_ugx / meter.manager.priceperunit.price)
    payload = payloads.GetToken(meter, num_token_units)
    meter_api = MeterAPIFactoryImpl.create_api(create_meter_manufacturer_hash(meter.manufacturer.name))
    token = meter_api.get_token(payload)
    return token

    
def log_token(user, meter, token, gross_amount_ugx):
    name = "%s %s" %(user.first_name, user.last_name)
    token_log = TokenLog.objects.create(name=name, user=user, token_no=token["token"], amount_paid=gross_amount_ugx, num_token_units=token["num_of_units"], meter=meter)
    return token_log

def get_price_category_payload(price_category):
    return payloads.NewPriceCategory(price_category)

def is_price_category_registered_with_manufacturer(price_category, manufacturer):
    # Do we have any meters for this manufacturer
    meters_for_manufacturer = Meter.objects.filter(manufacturer=manufacturer)
    if meters_for_manufacturer.exists():
        return True
    return False

def register_price_category(manufacturer, price_category):
    if not is_price_category_registered_with_manufacturer(price_category, manufacturer):
        payload = get_price_category_payload(price_category)
        meter_api = MeterAPIFactoryImpl.create_api(create_meter_manufacturer_hash(manufacturer.name))
        meter_api.register_price_category(payload)

def get_new_meter_customer_payload(meter, meter_owner):
    payload = payloads.NewMeterCustomer(meter, meter_owner)
    return payload

def register_meter_customer(meter, meter_owner):
    payload = get_new_meter_customer_payload(meter, meter_owner)
    meter_api = MeterAPIFactoryImpl.create_api(create_meter_manufacturer_hash(meter.manufacturer.name))
    return meter_api.register_meter_customer(payload)
    
class MeterListView(AdminOrSuperAdminRequiredMixin, ListView):
    template_name = "meter/list_meters.html.development"
    context_object_name = "meters"
    model = Meter
    
    
class MeterCreateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Meter
    template_name = "meter/create_meter.html.development"
    fields = "__all__"
    success_url = reverse_lazy("register_meter")
    success_message = "Meter: %(meter_no)s registered successfully."
    
    def get_success_message(self, cleaned_data):
        # Make the meter number accessible in the success_message
        return self.success_message % dict(
            cleaned_data,
            meter_no=self.object.meter_no,
        )

    def form_valid(self, form):
        # Register meter with the remote meter api before registering it locally
        meter = Meter(**form.cleaned_data)
        meter_owner = meter.manager
        price_category = meter.manager.priceperunit
  
        try:
            register_meter_customer(meter, meter_owner)
        except MeterAPIException as e:
            messages.error(self.request, "Remote API meter registration failed")
            return super(MeterCreateView, self).form_invalid(form)
        
        return super(MeterCreateView, self).form_valid(form)
    

    
class MeterEditView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Meter
    template_name = "meter/edit_meter.html.development"
    fields = "__all__"
    success_message = "Changes saved successfully."

    def get_success_url(self):
        url = reverse_lazy("edit_meter", kwarrgs={"pk":self.object.id})
        return url
    
class MeterCategoryCreateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = MeterCategory
    template_name = "meter/register_meter_category.html.development"
    fields = "__all__"
    success_url = reverse_lazy("register_meter_category") # change this
    success_message = "Meter Category: %(label)s registered successfully."
    
    def get_success_message(self, cleaned_data):
        # Make the meter number accessible in the success_message
        return self.success_message % dict(
            cleaned_data
        ) 
    
@user_passes_test(is_admin_or_super_admin)
def delete_meter(request, pk):
    num_of_meters_deleted, deleted_meter = Meter.objects.filter(id=pk).delete()
    if num_of_meters_deleted == 0:
        raise Http404("Meter doesnot exist")

    messages.success(request, "Meter has been deleted successfully")
    return redirect("list_meters")

def unlink_meter(request, pk):
    num_of_meters_updated = Meter.objects.filter(id=pk).update(manager=None)
    if num_of_meters_updated == 0:
        raise Http404()
    messages.success(request, "Meter has been unlinked successfully")
    return redirect("list_meters")




class BuyToken(View):

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")
        if user_id:
            meter = get_object_or_404(Meter, pk=user_id)
            buy_token_form = BuyTokenForm(initial={"meter_no": meter.meter_no})
        else:
            buy_token_form = BuyTokenForm()
        
        return render(request, "meter/buy_token.html.development", {"form": buy_token_form})


    def post(self, request, *args, **kwargs):
        buy_token_form = BuyTokenForm(request.POST)
        if buy_token_form.is_valid():
            meter = get_object_or_404(Meter, meter_no=buy_token_form.cleaned_data["meter_no"])
            
            gross_amount_ugx = buy_token_form.cleaned_data.get("amount")
            token = get_token(meter, gross_amount_ugx)
            log_token(request.user, meter, token, gross_amount_ugx)
                    
            """ TODO: Send SMS to user with token number """
            messages.success(request, "Token: %s Units: %s" %(token["token"], token["num_of_units"]))
                
        return render(request, "meter/buy_token.html.development", {"form": buy_token_form})
        
