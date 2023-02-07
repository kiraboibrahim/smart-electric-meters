import django_filters
from search_views.filters import BaseFilter

from .models import RechargeToken


class RechargeTokenListFilter(django_filters.FilterSet):
    from_ = django_filters.DateFilter(field_name="generated_at", lookup_expr="gt")
    to = django_filters.DateFilter(field_name="generated_at", lookup_expr="lt")
    manufacturer = django_filters.NumberFilter(field_name="meter__manufacturer", lookup_expr="exact")

    class Meta:
        model = RechargeToken
        fields = ["generated_at", "meter__manufacturer"]


class RechargeTokenSearchUrlQueryKwargMapping(BaseFilter):
    search_fields = {
        "query": {
            "operator": "__icontains",
            "fields": ["token_no", "meter__meter_no"]
        }
    }
