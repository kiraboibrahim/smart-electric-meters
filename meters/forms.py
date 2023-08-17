from functools import cached_property

from django import forms
from django.contrib.auth import get_user_model

from .models import Meter


User = get_user_model()


class MeterCreateForm(forms.ModelForm):
    skip_vendor_registration = forms.BooleanField(required=False)

    class Meta:
        model = Meter
        exclude = ("is_active", "is_registered_with_vendor", "created_at", "previous_vendor_registrations")

    def save(self, commit=True):
        skip_vendor_registration = self.cleaned_data.pop("skip_vendor_registration")
        meter = super().save(commit)
        if not skip_vendor_registration:
            meter.register()
        return meter


class MeterUpdateForm(forms.ModelForm):

    class Meta:
        model = Meter
        exclude = ("is_active", "is_created", "is_registered_with_vendor", "previous_vendor_registrations")


class MeterRechargeForm(forms.Form):
    meter_number = forms.CharField(max_length=11)
    recharge_amount = forms.IntegerField(widget=forms.TextInput(attrs={"type": "number", "placeholder": "UGX"}))
    applied_unit_price = forms.IntegerField(widget=forms.TextInput(attrs={"type": "number"}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if self.user.is_manager():
            self.fields["applied_unit_price"].widget.attrs = {"readonly": "readonly", "disabled": "disabled"}

    def clean(self):
        cleaned_data = super().clean()
        if not self.meter:
            self.add_error("meter_number", "Meter doesn't exist")
        elif not self.meter.is_active:
            self.add_error("meter_number", "Meter is not active")
        elif not self.meter.is_registered_with_vendor:
            self.add_error("meter_number", "Meter is not registered with vendor")
        else:
            cleaned_data["meter"] = self.meter
        return cleaned_data

    @cached_property
    def meter(self):
        meter_number = self.cleaned_data["meter_number"]
        return Meter.objects.filter(meter_number=meter_number).select_related().first()

    def recharge(self):
        applied_unit_price = self.meter.manager_unit_price if self.user.is_manager() else \
            self.cleaned_data["applied_unit_price"]
        recharge_amount = self.cleaned_data["recharge_amount"]
        return self.meter.recharge(recharge_amount, applied_unit_price=applied_unit_price)

