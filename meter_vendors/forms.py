from django import forms

from phonenumber_field.widgets import PhoneNumberPrefixWidget

from core import COUNTRY_CHOICES

from .models import MeterVendor


class MeterVendorCreateForm(forms.ModelForm):

    class Meta:
        model = MeterVendor
        fields = "__all__"
        widgets = {
            "phone_no": PhoneNumberPrefixWidget(country_choices=COUNTRY_CHOICES)
        }


class MeterVendorUpdateForm(forms.ModelForm):
    class Meta:
        model = MeterVendor
        fields = "__all__"
        widgets = {
            "phone_no": PhoneNumberPrefixWidget(country_choices=COUNTRY_CHOICES)
        }
