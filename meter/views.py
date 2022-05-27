import uuid
import time
import math

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

from meter.utils import is_admin, is_super_admin, is_admin_or_super_admin, SuperAdminRequiredMixin, AdminRequiredMixin, AdminOrSuperAdminRequiredMixin
from meter.models import MeterCategory, Meter, TokenHistory
from meter.api import MobileMoneyApiFactory, MeterApiFactory
from meter.forms import BuyTokenForm
from meter.payload import NewCustomer, VendingMeter, RequestToPay, NewPrice

from transaction.models import Transaction

# Create your views here.
User = get_user_model()


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


def buy_token(request, pk=None):
    timeout = 10
    if request.method == "POST":
        form = BuyTokenForm(request.POST)
        if form.is_valid():
            meter_no = form.cleaned_data.get("meter_no")
            meter = get_object_or_404(Meter, meter_no=meter_no)
            mtn_momo = MobileMoneyApiFactory.create_api("mtn")
            phone_no = form.cleaned_data["phone_no"]
            amount = form.cleaned_data["amount"]
            external_id = str(uuid.uuid4())
            ref = str(uuid.uuid4())
            payload = RequestToPay(phone_no, amount, external_id, ref)
            mtn_momo.request_to_pay(payload)

            while timeout > 0:
                state = mtn_momo.request_transaction_status(ref)

                if state == 2 or state == 4:
                    break
                time.sleep(1)
                timeout -= 1

            # Successful Transaction
            if state == 2: 
                percentage_charge = meter.meter_category.percentage_charge
                fixed_charge = meter.meter_category.fixed_charge
                total_charge = math.ceil(((percentage_charge / 100) * amount) + fixed_charge)
                original_amount = amount
                amount -= total_charge
                payload = VendingMeter(meter, amount)

                meter_api = MeterApiFactory.create_api(meter.manufacturer.name.title().strip().replace(" ", ""))
                token = meter_api.get_token(payload)

                result = 0 if token == {} else 1
                # Log transaction whether failed or successful
                transaction = Transaction.objects.create(external_id=external_id, charge=total_charge, amount=original_amount, phone_no=phone_no, state=result)
                transaction.save()

                # Log token if only the result was success
                if result:
                    name = "%s %s" %(request.user.first_name, request.user.last_name)
                    token_log = TokenHistory.objects.create(name=name, user=request.user, token_no=token["token"], phone_no=phone_no, amount_paid=original_amount, num_token_units=token["num_of_units"], meter=meter)
                    token_log.save()
                    # Send SMS and alert user through user interface
                    messages.success(request, "Token: %s, Units: %s" %(token["token"], token["num_of_units"]))
                else:
                    messages.error(request, "Sorry, this is our fault, Reach to us via our helpline.")
            else:
                # Failed Mobile Money Transaction
                messages.error(request, "Insufficient funds on mobile wallet or Request timed out.")
                
        return render(request, "meter/buy_token.html.development", {"form": form})
                
    else:
        if pk:
            meter = get_object_or_404(Meter, pk=pk)
            form = BuyTokenForm(initial={"meter_no": meter.meter_no})
        else:
            form = BuyTokenForm()
        
        return render(request, "meter/buy_token.html.development", {"form": form})
