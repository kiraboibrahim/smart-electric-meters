from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from search_views.filters import build_q

from prepaid_meters_token_generator_system.views.mixins import SearchMixin

from payment.models import Payment
from payment.utils import get_list_payments_template_context_data
from payment.filters import PaymentSearchFilter, PaymentListFilter


class BasePaymentListView(ListView):
    model = Payment
    template_name = "payment/list_payments.html.development"
    context_object_name = "payments"

    def get_context_data(self, **kwargs):
        base_context = super(BasePaymentListView, self).get_context_data(**kwargs)
        context = get_list_payments_template_context_data(self.request, base_context)
        return context


class PaymentListView(LoginRequiredMixin, BasePaymentListView):
    pass


class PaymentSearchView(LoginRequiredMixin, SearchMixin, BasePaymentListView):
    search_filters_class = PaymentSearchFilter

    def get_queryset(self):
        payments = super(PaymentSearchView, self).get_queryset()
        search_filters = self.get_search_filters()
        payments = payments.filter(search_filters)
        return payments
