import django_filters

from .models import MeterVendor


class MeterVendorFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = MeterVendor
        fields = ("name", )

