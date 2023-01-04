import math
from functools import cached_property

from django import forms
from django.contrib.auth import get_user_model

from users.account_types import MANAGER

from meter_categories.models import MeterCategory

from manufacturers.models import MeterManufacturer

from .models import Meter


User = get_user_model()


class AddMeterForm(forms.ModelForm):
    is_registered = forms.BooleanField(label="Already registered with manufacturer", required=False)

    class Meta:
        model = Meter
        exclude = ("is_active", )
        labels = {
            "meter_no": "Meter number",
        }
        

class EditMeterForm(AddMeterForm):
    pass
                

class AdminMeterFiltersForm(forms.Form):
    is_active_field_choices = [
        (True, "Active"),
        (False, "Inactive"),
    ]
    manufacturer = forms.ModelChoiceField(queryset=MeterManufacturer.objects.all(), empty_label="All", required=False)
    category = forms.ModelChoiceField(queryset=MeterCategory.objects.all(), empty_label="All", required=False)
    manager = forms.ModelChoiceField(queryset=User.objects.all().filter(account_type=MANAGER), empty_label="All",
                                     required=False)
    is_active = forms.ChoiceField(label="Status", choices=is_active_field_choices, required=False)


class ManagerMeterFiltersForm(forms.Form):
    is_active_field_choices = [
        (True, "Active"),
        (False, "Inactive"),
    ]
    manufacturer = forms.ModelChoiceField(queryset=MeterManufacturer.objects.all(), empty_label="All", required=False)
    is_active = forms.ChoiceField(label="Status", choices=is_active_field_choices, required=False)


class RechargeMeterForm(forms.Form):

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user.is_manager():
            self.fields["price_per_unit"].disabled = True

    meter_no = forms.CharField(max_length=11, label="Meter number")
    gross_recharge_amount = forms.IntegerField(label="Recharge amount",
                                               widget=forms.TextInput(attrs={"type": "number"}))
    price_per_unit = forms.IntegerField()

    def clean(self):
        gross_recharge_amount = self.cleaned_data.get("gross_recharge_amount")
        meter = self.meter
        if meter is None:
            self.add_error("meter_no", "Meter not found")
        else:
            self.cleaned_data["meter"] = meter
            minimum_recharge_amount = self.get_meter_minimum_recharge_amount(meter)
            if gross_recharge_amount <= minimum_recharge_amount:
                self.add_error("gross_recharge_amount", "Amount should be greater than %d" % minimum_recharge_amount)
        return self.cleaned_data

    @cached_property
    def meter(self):
        meter_no = self.cleaned_data["meter_no"]
        meter = Meter.objects.filter(meter_no=meter_no).select_related()
        if len(meter) != 1:
            return None
        return meter[0]

    @staticmethod
    def get_meter_minimum_recharge_amount(meter):
        percentage_charge, fixed_charge = meter.category.charges
        minimum_recharge_amount = math.ceil(fixed_charge / (1 - percentage_charge))
        return minimum_recharge_amount

    def recharge(self, is_manager=True):
        gross_recharge_amount = self.cleaned_data["gross_recharge_amount"]
        price_per_unit = self.cleaned_data["price_per_unit"]
        if is_manager:
            price_per_unit = self.meter.unit_price
        return self.meter.recharge(gross_recharge_amount, price_per_unit)
