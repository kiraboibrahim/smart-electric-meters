from django import forms


class PaymentFiltersForm(forms.Form):
    from_ = forms.DateField(widget=forms.TextInput({"type": "date"}), required=False)
    to = forms.DateField(widget=forms.TextInput({"type": "date"}), required=False)
