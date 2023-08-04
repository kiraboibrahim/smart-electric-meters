from collections import OrderedDict

import django_filters

from core.fields import Select2Field

from .models import Meter


class MeterFilter(django_filters.FilterSet):
    meter_number = django_filters.CharFilter(field_name="meter_number", lookup_expr="contains")

    class Meta:
        model = Meter
        fields = ['meter_number', 'vendor', 'manager', 'is_active']

    def get_form_class(self):
        base_form_class = super().get_form_class()

        class FormClass(base_form_class):
            if self.request.user.is_manager():
                manager = None
        return FormClass

    @property
    def qs(self):
        meters = super().qs
        return meters.for_user(self.request.user)
