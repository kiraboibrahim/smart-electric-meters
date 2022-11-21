from payment.models import Payment
from payment.forms import PaymentFiltersForm

from prepaid_meters_token_generator_system.forms import SearchForm
from prepaid_meters_token_generator_system.utils.paginator import paginate_queryset, get_page_number

from user.account_types import MANAGER

from payment.filters import PaymentListFilter


def apply_user_filter(logged_in_user, payments):
    if logged_in_user.account_type == MANAGER:
        return payments.filter(user=logged_in_user)

    return payments


def apply_date_range_filter(request, payments):
    payments = PaymentListFilter(request.GET, queryset=payments).qs
    return payments


def get_list_payments_template_forms(request, context):
    default_payment_search_form = SearchForm(request.GET)
    default_payment_filters_form = PaymentFiltersForm(request.GET)
    payment_search_form = context.get("payment_search_form", default_payment_search_form)
    payment_filters_form = context.get("payment_filters_form", default_payment_filters_form)
    return payment_search_form, payment_filters_form


def get_payments(request, context):
    logged_in_user = request.user
    payments = context.get("payments")
    payments = apply_date_range_filter(request, apply_user_filter(logged_in_user, payments))
    return payments


def get_list_payments_template_context_data(request, base_context={}):
    payment_search_form, payment_filters_form = get_list_payments_template_forms(request, base_context)
    payments = get_payments(request, base_context)

    paginator = paginate_queryset(payments)
    requested_page_number = get_page_number(request)
    page_obj = paginator.get_page(requested_page_number)

    base_context["payments"] = page_obj.object_list
    base_context["page_obj"] = page_obj
    base_context["payment_search_form"] = payment_search_form
    base_context["payment_filters_form"] = payment_filters_form

    return base_context
