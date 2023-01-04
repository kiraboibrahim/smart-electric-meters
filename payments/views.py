from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

from shared.views import SearchListView, FilterListView
from shared.forms import SearchForm as PaymentSearchForm

from .models import Payment
from .filters import PaymentSearchQueryParameterMapping, PaymentTimeRangeFilter
from .forms import PaymentFiltersForm
from .utils import get_user_payments


class PaymentListView(LoginRequiredMixin, FilterListView):
    model = Payment
    template_name = "payments/list_payments.html.development"
    context_object_name = "payments"
    paginate_by = settings.MAX_ITEMS_PER_PAGE
    model_list_filter_class = PaymentTimeRangeFilter

    def get_template_names(self):
        if self.request.user.is_manager():
            return "managers/payments/list_payments.html.development"
        return self.template_name

    def get_queryset(self):
        payments = super().get_queryset()
        payments = get_user_payments(self.request.user, initial_payments=payments)
        return payments

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["payment_filters_form"] = PaymentFiltersForm(self.request.GET)
        context["payment_search_form"] = PaymentSearchForm(self.request.GET)
        return context


class PaymentSearchView(LoginRequiredMixin, SearchListView):
    model = Payment
    template_name = "payments/list_payments.html.development"
    context_object_name = "payments"
    paginate_by = settings.MAX_ITEMS_PER_PAGE
    search_query_parameter_mapping_class = PaymentSearchQueryParameterMapping
    model_fields_filter_class = PaymentTimeRangeFilter

    def get_queryset(self):
        payments = super(PaymentSearchView, self).get_queryset()
        return get_user_payments(self.request.user, initial_payments=payments)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["payment_filters_form"] = PaymentFiltersForm(self.request.GET)
        context["payment_search_form"] = PaymentSearchForm(self.request.GET)
        return context
