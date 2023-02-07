import math
from functools import cached_property

from django import forms
from django.contrib.auth import get_user_model

from manufacturers.models import MeterManufacturer
from meter_categories.models import MeterCategory
from users.account_types import MANAGER
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
        self.user = user
        super().__init__(*args, **kwargs)
        if self.user.is_manager():
            self.fields["price_per_unit"].disabled = True

    meter_no = forms.CharField(max_length=11, label="Meter number")
    gross_recharge_amount = forms.IntegerField(label="Recharge amount",
                                               widget=forms.TextInput(attrs={"type": "number"}))
    price_per_unit = forms.IntegerField()

    def clean(self):
        gross_recharge_amount = self.cleaned_data.get("gross_recharge_amount")
        if self.meter is None:
            self.add_error("meter_no", "Meter not found")
        else:
            self.cleaned_data["meter"] = self.meter  # Add meter to cleaned data to be retrieved by view
            if gross_recharge_amount <= self.minimum_recharge_amount:
                self.add_error("gross_recharge_amount", "Amount should be greater than %d" %
                               self.minimum_recharge_amount)
        return self.cleaned_data

    @cached_property
    def meter(self):
        meter_no = self.cleaned_data["meter_no"]
        return Meter.objects.filter(meter_no=meter_no).select_related().first()

    @property
    def minimum_recharge_amount(self):
        percentage_charge, fixed_charge = self.meter.category.charges
        return math.ceil(fixed_charge / (1 - percentage_charge))

    def recharge(self):
        gross_recharge_amount = self.cleaned_data["gross_recharge_amount"]
        price_per_unit = self.cleaned_data["price_per_unit"]
        if self.user.is_manager:
            # Change the price unit to the one of the manager instead of the one given in the form
            price_per_unit = self.meter.unit_price
        return self.meter.recharge(gross_recharge_amount, price_per_unit)
