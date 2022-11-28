from django import forms

from manufacturers.models import MeterManufacturer


class RechargeTokenFiltersForm(forms.Form):
    from_ = forms.DateField(widget=forms.TextInput({"type": "date"}), required=False)
    to = forms.DateField(widget=forms.TextInput({"type": "date"}), required=False)
    manufacturer = forms.ModelChoiceField(queryset=MeterManufacturer.objects.all(), empty_label="All",
                                     required=False)
