import math

from django import forms

from meter import models as meter_models


class AddMeterForm(forms.ModelForm):

    class Meta:
        model = meter_models.Meter
        exclude = ["is_active"]
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
        
class RechargeMeterForm(forms.Form):
    meter_no = forms.CharField(max_length=11, label="Meter Number")
    amount = forms.IntegerField(widget=forms.TextInput(attrs={"type": "number", "placeholder": "5000"}))
        
    def clean(self):
        meter = None
        meter_no = self.cleaned_data.get("meter_no")
        amount = self.cleaned_data.get("amount")

        try:
            meter = Meter.objects.get(meter_no=meter_no)
        except Meter.DoesNotExist:
            self.add_error("meter_no", "Meter not found")
        else:
            self.meter = meter

            percentage_charge = meter.category.percentage_charge / 100
            fixed_charge = meter.category.fixed_charge
            min_amount = math.ceil(fixed_charge / (1 - percentage_charge))
        
            if amount <= min_amount:
                self.add_error("amount", "Amount should be greater than %d" %(min_amount))
            
        return self.cleaned_data

        
