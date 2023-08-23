from django import forms
from django.contrib.auth import get_user_model

import django_filters

from .models import Meter

User = get_user_model()


class MeterFilter(django_filters.FilterSet):
    meter_number = django_filters.CharFilter(field_name="meter_number", lookup_expr="contains")

    class Meta:
        model = Meter
        fields = ['meter_number', 'vendor', 'manager', 'is_active']

    def get_form_class(self):
        user_is_manager = self.request.user.is_manager()
        BaseFormClass = super().get_form_class()

        class FormClass(BaseFormClass):
            manager = forms.ModelChoiceField(queryset=User.objects.all_managers(), required=False,
                                             empty_label="No manager selected",
                                             widget=forms.Select(attrs={"id": "meter-filter__manager"}))

            if user_is_manager:
                manager = None  # Managers are not allowed to filter by this field

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.fields["vendor"].empty_label = "No vendor selected"
                is_active_choices = [("", "No state selected")] + list(self.fields["is_active"].widget.choices)[1:]
                self.fields["is_active"].widget.choices = is_active_choices

        return FormClass

    @property
    def qs(self):
        meters = super().qs
        return meters.for_user(self.request.user)
