from django.conf import settings

from prepaid_meters_token_generator_system.utils.paginator import paginate_queryset, get_page_number
from prepaid_meters_token_generator_system.forms import SearchForm

from user.account_types import MANAGER, SUPER_ADMIN, ADMIN

from meter.models import Meter
from meter.forms import AddMeterForm, MeterFiltersForm
from meter.filters import MeterListFilter

from meter_category.forms import AddMeterCategoryForm


MAX_ITEMS_PER_PAGE = settings.MAX_ITEMS_PER_PAGE


def apply_user_filters(logged_in_user, meters):
    if logged_in_user.account_type == MANAGER:
        meters.filter(manager=logged_in_user)
    return meters


def get_list_meters_template_forms(request, context):
    add_meter_form = context.get("add_meter_form", AddMeterForm())
    add_meter_category_form = context.get("add_meter_category_form", AddMeterCategoryForm())
    search_meter_form = context.get("search_meter_form", SearchForm(request.GET))
    return add_meter_form, add_meter_category_form, search_meter_form


def get_list_meters_template_context_data(request, base_context={}):
    """
        Defines the context variables required in the list_meters template
    """
    logged_in_user = request.user

    add_meter_form, add_meter_category_form, search_meter_form = get_list_meters_template_forms(request, base_context)
    filters_form = MeterFiltersForm(request.GET)

    meter_queryset = apply_user_filters(logged_in_user, base_context.get("meters", Meter.objects.all()))
    # Apply field filters to the queryset
    meter_queryset = MeterListFilter(request.GET, queryset=meter_queryset).qs
    
    paginator = paginate_queryset(meter_queryset, MAX_ITEMS_PER_PAGE)
    page_number = get_page_number(request)
    page = paginator.page(page_number)

    base_context["meters"] = page.object_list
    base_context["paginator"] = paginator
    base_context["page_obj"] = page
    base_context["add_meter_form"] = add_meter_form
    base_context["add_meter_category_form"] = add_meter_category_form
    base_context["search_meter_form"] = search_meter_form
    base_context["filters_form"] = filters_form
    return base_context
