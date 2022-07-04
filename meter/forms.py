import math

from django import forms
from django.shortcuts import get_object_or_404
from meter.models import Meter


class CreateMeterForm(forms.ModelForm):

    class Meta:
        model = Meter
        fields = "__all__"


class EditMeterForm(CreateMeterForm):
    pass
                

class BuyTokenForm(forms.Form):
    meter_no = forms.CharField(max_length=11, label="Meter Number")
    amount = forms.IntegerField(help_text="Local tax rates may apply", widget=forms.TextInput(attrs={"type": "number", "placeholder": "5000"}))


    def clean(self):
        meter_no = self.cleaned_data.get("meter_no")
        amount = self.cleaned_data.get("amount")
        meter = get_object_or_404(Meter, meter_no=meter_no)
        percentage_charge = meter.category.percentage_charge/100
        min_amount = math.ceil(meter.category.fixed_charge / (1 - percentage_charge))

        if not meter.manager:
            self.add_error("meter_no", "This meter is orphaned. ie It has no manager")
        
        if amount <= min_amount:
            self.add_error("amount", "Amount should be greater than %d" %(min_amount))
        return self.cleaned_data

        
