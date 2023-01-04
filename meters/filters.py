import django_filters
from search_views.filters import BaseFilter

from .models import Meter


class AdminMeterListFilter(django_filters.FilterSet):

    class Meta:
        model = Meter
        fields = ['manufacturer', 'category', 'manager', 'is_active']


class ManagerMeterListFilter(django_filters.FilterSet):

    class Meta:
        model = Meter
        fields = ['manufacturer', 'is_active']


class MeterSearchQueryParameterMapping(BaseFilter):
    search_fields = {
        "query": {
            "operator": "__icontains",
            "fields": ["meter_no"]
        }
    }
