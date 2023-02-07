from django import forms

from manufacturers.models import MeterManufacturer
from shared.widgets import DateInput


class RechargeTokenFiltersForm(forms.Form):
    from_ = forms.DateField(widget=DateInput, required=False)
    to = forms.DateField(widget=DateInput, required=False)
    manufacturer = forms.ModelChoiceField(queryset=MeterManufacturer.objects.all(), empty_label="All",
                                          required=False)
