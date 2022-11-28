from search_views.filters import BaseFilter
import django_filters

from .models import Payment


class PaymentTimeRangeFilter(django_filters.FilterSet):
    from_ = django_filters.DateFilter(field_name="paid_at", lookup_expr="gt")
    to = django_filters.DateFilter(field_name="paid_at", lookup_expr="lt")

    class Meta:
        model = Payment
        fields = ['paid_at']


class PaymentSearchQueryParameterMapping(BaseFilter):
    search_fields = {
        "query": {
            "operator": "__icontains",
            "fields": ["user__phone_no", "user__first_name", "user__last_name"]
        }
    }
