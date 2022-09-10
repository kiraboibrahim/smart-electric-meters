from django import forms

from meter_manufacturer.models import MeterManufacturer


class AddMeterManufacturerForm(forms.ModelForm):

    class Meta:
        model = MeterManufacturer
        fields = "__all__"
        labels = {
            "name": "Company name",
        }


class MeterManufacturerSearchForm(forms.Form):
    query = forms.CharField()
