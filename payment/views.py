from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from search_views.filters import build_q

from prepaid_meters_token_generator_system.utils.forms import SearchForm

from payment.models import Payment
from payment.utils import get_payments


class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = "payment/list_payments.html.development"
    context_object_name = "payments"

    def get_queryset(self):
        logged_in_user = self.request.user
        return get_payments(logged_in_user)

    def get_context_data(self, **kwargs):
        context = super(PaymentListView, self).get_context_data(**kwargs)
        context["search_payment_form"] = SearchForm(self.request.GET)
        return context


class PaymentSearchView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = "payment/list_payments.html.development"
    context_object_name = "payments"
