from search_views.filters import BaseFilter
import django_filters


from payments.models import Payment


class PaymentListFilter(django_filters.FilterSet):
    from_ = django_filters.DateFilter(field_name="paid_at", lookup_expr="gt")
    to = django_filters.DateFilter(field_name="paid_at", lookup_expr="lt")

    class Meta:
        model = Payment
        fields = ['paid_at']


class PaymentSearchFieldMapping(BaseFilter):
    search_fields = {
        "query": {
            "operator": "__icontains",
            "fields": ["user__phone_no", "user__first_name", "user__last_name"]
        }
    }
