import math

from django import forms
from django.contrib.auth import get_user_model

from prepaid_meters_token_generator_system.utils.forms import BaseFiltersForm
from prepaid_meters_token_generator_system.utils.forms import BaseSearchForm
from meter import models as meter_models
from user.account_types import MANAGER

User = get_user_model()
is_active_field_choices = [
    (1, "Active"),
    (0, "Inactive"),
]

class AddMeterForm(forms.ModelForm):
    is_registered = forms.BooleanField(label="Already registered with manufacturer", required=False)
    class Meta:
        model = meter_models.Meter
        exclude = ("is_active", )
        labels = {
            "meter_no": "Meter Number",
        }
        

class EditMeterForm(AddMeterForm):
    pass
                


class AddMeterCategoryForm(forms.ModelForm):

    class Meta:
        model = meter_models.MeterCategory
        fields = "__all__"

        
class AddMeterManufacturerForm(forms.ModelForm):

    class Meta:
        model = meter_models.Manufacturer
        fields = "__all__"
        labels = {
            "name": "Company name",
        }

class Filters(BaseFiltersForm):
    manufacturer = forms.ModelChoiceField(queryset=meter_models.Manufacturer.objects.all(), empty_label="All", required=False)
    category = forms.ModelChoiceField(queryset=meter_models.MeterCategory.objects.all(), empty_label="All", required=False)
    manager = forms.ModelChoiceField(queryset=User.objects.all().filter(account_type=MANAGER), empty_label="All", required=False)
    is_active = forms.ChoiceField(label="State", choices=is_active_field_choices, required=False)
        

class SearchForm(BaseSearchForm):
    model_search_field = "meter_no"
    

    
   
class RechargeMeterForm(forms.Form):
    meter_no = forms.CharField(max_length=11, label="Meter Number")
    amount = forms.IntegerField(widget=forms.TextInput(attrs={"type": "number", "placeholder": "5000"}))
        
    def clean(self):
        meter = None
        meter_no = self.cleaned_data.get("meter_no")
        amount = self.cleaned_data.get("amount")

        try:
            meter = meter_models.Meter.objects.get(meter_no=meter_no)
        except meter_models.Meter.DoesNotExist:
            self.add_error("meter_no", "Meter not found")
        else:
            self.meter = meter

            percentage_charge = meter.category.percentage_charge / 100
            fixed_charge = meter.category.fixed_charge
            min_amount = math.ceil(fixed_charge / (1 - percentage_charge))
        
            if amount <= min_amount:
                self.add_error("amount", "Amount should be greater than %d" %(min_amount))
            
        return self.cleaned_data

        
