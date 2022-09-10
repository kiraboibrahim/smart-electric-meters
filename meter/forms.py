import math

from django import forms
from django.contrib.auth import get_user_model

from user.account_types import MANAGER

from meter.models import Meter

from meter_category.models import MeterCategory

from meter_manufacturer.models import MeterManufacturer


User = get_user_model()

is_active_field_choices = [
    (1, "Active"),
    (0, "Inactive"),
]

class AddMeterForm(forms.ModelForm):
    is_registered = forms.BooleanField(label="Already registered with manufacturer", required=False)
    class Meta:
        model = Meter
        exclude = ("is_active", )
        labels = {
            "meter_no": "Meter Number",
        }
        

        
class EditMeterForm(AddMeterForm):
    pass
                


class MeterFiltersForm(forms.Form):
    manufacturer = forms.ModelChoiceField(queryset=MeterManufacturer.objects.all(), empty_label="All", required=False)
    category = forms.ModelChoiceField(queryset=MeterCategory.objects.all(), empty_label="All", required=False)
    manager = forms.ModelChoiceField(queryset=User.objects.all().filter(account_type=MANAGER), empty_label="All", required=False)
    is_active = forms.ChoiceField(label="State", choices=is_active_field_choices, required=False)
        

class SearchMeterForm(forms.Form):
    query = forms.CharField(required=False)
    

    
   
class RechargeMeterForm(forms.Form):
    meter_no = forms.CharField(max_length=11, label="Meter Number")
    amount = forms.IntegerField(widget=forms.TextInput(attrs={"type": "number", "placeholder": "5000"}))
        
    def clean(self):
        meter = None
        meter_no = self.cleaned_data.get("meter_no")
        amount = self.cleaned_data.get("amount")

        try:
            meter = meter_models.Meter.objects.get(meter_no=meter_no)
        except Meter.DoesNotExist:
            self.add_error("meter_no", "Meter not found")
        else:
            self.meter = meter

            percentage_charge, fixed_charge = meter.category.charges
            min_amount = math.ceil(fixed_charge / (1 - percentage_charge))
        
            if amount <= min_amount:
                self.add_error("amount", "Amount should be greater than %d" %(min_amount))
            
        return self.cleaned_data

        
