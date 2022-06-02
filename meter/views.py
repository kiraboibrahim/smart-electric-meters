import uuid
import time
import math
import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.conf import settings
from django.views import View

from meter.utils import is_admin, is_super_admin, is_admin_or_super_admin, SuperAdminRequiredMixin, AdminRequiredMixin, AdminOrSuperAdminRequiredMixin, create_meter_manufacturer_hash
from meter.models import MeterCategory, Meter, Manufacturer, TokenHistory
from meter.api import MobileMoneyAPIFactoryImpl, MeterAPIFactoryImpl
from meter.forms import BuyTokenForm
from meter import payloads

from transaction.models import Transaction

from user.acc_types import MANAGER
from user.models import PricePerUnit

# Create your views here.
User = get_user_model()
logger = logging.getLogger(__name__)
TRANSACTION_SUCCESSFUL = 2
TRANSACTION_FAILED = 4

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
        manufacturer = form.cleaned_data["manufacturer"]
        meter = Meter(**form.cleaned_data)
        payload = payloads.NewCustomer(meter)
        meter_api = MeterAPIFactoryImpl.create_api(create_meter_manufacturer_hash(manufacturer.name))
        result = meter_api.register_meter_customer(payload)
        if not result:
            messages.error(self.request, "Meter registration failed because remote meter API registration failed")
            return super(MeterCreateView, self).form_invalid(form)
        
        return super(MeterCreateView, self).form_valid(form)

    
    """ TODO: Initialize manager field with only managers """
    """ TODO: Register remotely with the company manufacturer API """
    

    
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
    meter = get_object_or_404(Meter, pk=pk)
    meter.delete()
    messages.success(request, "Meter: %s has been deleted successfully." %(meter.meter_no))
    return redirect("list_meters")

def unlink_meter(request, pk):
    meter = get_object_or_404(Meter, pk=pk)
    # Unlink the meter from the manager it was assigned
    meter.manager = None
    meter.save()
    messages.success(request, "Meter %s has been unlinked successfully" %(meter.meter_no))
    return redirect("list_meters")

def wait_for_mobile_money_transaction(mobile_money_api, transaction_reference):
    transaction_timeout = 300 # 5 minutes
    
    while transaction_timeout > 0:
        transaction_state = mobile_money_api.get_transaction_state(transaction_reference)

        if transaction_state == TRANSACTION_SUCCESSFUL or transaction_state == TRANSACTION_FAILED:
            break
        time.sleep(1)
        transaction_timeout -= 1
        
    return transaction_state 

def debit_funds(payload):
    mobile_money_api = MobileMoneyAPIFactoryImpl.create_api("mtn")
    mobile_money_api.debit_funds(payload)
    transaction_reference = payload.transaction_reference
    transaction_state = wait_for_mobile_money_transaction(mobile_money_api, transaction_reference)

    return transaction_state

def get_charges_ugx(meter, gross_amount_ugx):
    percentage_charge = meter.meter_category.percentage_charge
    fixed_charge_ugx = meter.meter_category.fixed_charge
    total_charges_ugx = math.ceil(((percentage_charge / 100) * gross_amount_ugx) + fixed_charge_ugx)
    return total_charges_ugx

def get_net_amount_ugx(meter, gross_amount_ugx):
    total_charges_ugx = get_charges_ugx(meter, gross_amount_ugx)
    net_amount_ugx = gross_amount_ugx - total_charges_ugx
    return net_amount_ugx, total_charges_ugx
    
def get_token(meter, gross_amount_ugx):
    net_amount_ugx = get_net_amount_ugx(meter, gross_amount_ugx)
    payload = payloads.GetToken(meter, net_amount_ugx)
    meter_api = MeterAPIFactoryImpl.create_api(create_meter_manufacturer_hash(meter.manufacturer.name))
    token = meter_api.get_token(payload)

    return token

def log_mobile_money_transaction(debit_payload, charge, transaction_state):
    state = 1 if transaction_state == TRANSACTION_SUCCESSFUL else 0
    print("="*50)
    print(state)
    transaction = Transaction.objects.create(external_id=debit_payload.transaction_id, charge=charge, amount=debit_payload.amount_ugx, phone_no=debit_payload.phone_no, state=state)
    return transaction

    
def log_token(user, meter, phone_no, token, gross_amount_ugx):
    name = "%s %s" %(user.first_name, user.last_name)
    token_log = TokenHistory.objects.create(name=name, user=user, token_no=token["token"], phone_no=phone_no, amount_paid=gross_amount_ugx, num_token_units=token["num_of_units"], meter=meter)
    return token_log

def get_debit_payload(cleaned_form_data):
    phone_no = cleaned_form_data["phone_no"]
    gross_amount_ugx = cleaned_form_data["amount"]
    transaction_id = str(uuid.uuid4())
    transaction_reference = str(uuid.uuid4())
    return payloads.DebitFunds(phone_no, gross_amount_ugx, transaction_id, transaction_reference)


class BuyToken(View):

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if pk:
            meter = get_object_or_404(Meter, pk=pk)
            form = BuyTokenForm(initial={"meter_no": meter.meter_no})
        else:
            form = BuyTokenForm()
        
        return render(request, "meter/buy_token.html.development", {"form": form})


    def post(self, request, *args, **kwargs):
        form = BuyTokenForm(request.POST)
        if form.is_valid():
            meter = get_object_or_404(Meter, meter_no=form.cleaned_data["meter_no"])
            debit_payload = get_debit_payload(form.cleaned_data)
            transaction_state = debit_funds(debit_payload)
            
            # Successful Transaction
            if transaction_state == TRANSACTION_SUCCESSFUL:
                gross_amount_ugx = form.cleaned_data.get("amount")
                # Log the mobile money transaction in order to follow up on failed token generation
                # Yet the mobile money transaction has been successful
                charges_ugx = get_charges_ugx(meter, gross_amount_ugx)
                log_mobile_money_transaction(debit_payload, charges_ugx, transaction_state)
                token = get_token(meter, gross_amount_ugx)
                phone_no = form.cleaned_data.get("phone_no")
                log_token(request.user, meter, phone_no, token, gross_amount_ugx)
                    
                """ TODO: Send SMS to user with token number """
                messages.success(request, "Token: %s, Units: %s" %(token["token"], token["num_of_units"]))
            else:
                messages.error(request, "Mobile money request has failed.")
                
        return render(request, "meter/buy_token.html.development", {"form": form})
        
