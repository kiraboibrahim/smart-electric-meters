from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

from shared.mixins import SearchMixin
from shared.forms import SearchForm as PaymentSearchForm

from payments.models import Payment
from payments.filters import PaymentSearchFieldMapping, PaymentListFilter
from payments.forms import PaymentFiltersForm

from users.account_types import MANAGER


class BasePaymentListView(ListView):
    model = Payment
    template_name = "payments/list_payments.html.development"
    context_object_name = "payments"
    paginate_by = settings.MAX_ITEMS_PER_PAGE

    def get_queryset(self):
        payments = super(BasePaymentListView, self).get_queryset()
        payments = PaymentListFilter(self.request.GET, queryset=payments).qs
        if self.request.user.account_type == MANAGER:
            payments = payments.filter(user=self.request.user)
        return payments

    def get_context_data(self, **kwargs):
        context = super(BasePaymentListView, self).get_context_data(**kwargs)
        context["payment_filters_form"] = PaymentFiltersForm(self.request.GET)
        context["payment_search_form"] = PaymentSearchForm(self.request.GET)
        return context


class PaymentListView(LoginRequiredMixin, BasePaymentListView):
    pass


class PaymentSearchView(LoginRequiredMixin, SearchMixin, BasePaymentListView):
    search_field_mapping = PaymentSearchFieldMapping

    def get_queryset(self):
        payments = super(PaymentSearchView, self).get_queryset()
        search_filters = self.get_search_filters()
        payments = payments.filter(search_filters)
        return payments

