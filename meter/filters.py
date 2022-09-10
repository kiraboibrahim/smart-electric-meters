from search_views.filters import BaseFilter
import django_filters


import meter.models as meter_models


class MeterListFilter(django_filters.FilterSet):

    class Meta:
        model = meter_models.Meter
        fields = ['manufacturer', 'category', 'manager', 'is_active']



class MeterSearchFilter(BaseFilter):
    search_fields = {
        "query": {
            "operator": "__icontains",
            "fields": ["meter_no"]
        }
    }
