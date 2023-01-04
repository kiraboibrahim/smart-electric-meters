from django import forms

from shared.widgets import DateInput


class PaymentFiltersForm(forms.Form):
    from_ = forms.DateField(widget=DateInput, required=False)
    to = forms.DateField(widget=DateInput, required=False)
