from django.conf import settings

from prepaid_meters_token_generator_system.utils.paginator import paginate_queryset, get_page_number
from user.account_types import MANAGER

from meter.models import Meter
from meter.forms import AddMeterForm, SearchMeterForm, MeterFiltersForm
from meter.filters import MeterListFilter

from meter_manufacturer.forms import AddMeterManufacturerForm

from meter_category.forms import AddMeterCategoryForm


MAX_ITEMS_PER_PAGE = settings.MAX_ITEMS_PER_PAGE


def get_meter_manufacturer_hash(manufacturer_name):
    return manufacturer_name.title().strip().replace(" ", "")


def get_meter_queryset(authenticated_user):
    queryset = Meter.objects.all()
    if authenticated_user.account_type == MANAGER:
        queryset = queryset.filter(manager=authenticated_user)
        
    return queryset


def get_list_meters_template_context_data(request, base_context={}):
    """
    Defines the context variables required in the list_meters template 
    """

    authenticated_user = request.user
    
    add_meter_form = base_context.get("add_meter_form", AddMeterForm())
    add_meter_category_form = base_context.get("add_meter_category_form", AddMeterCategoryForm())
    search_meter_form = base_context.get("search_meter_form", SearchMeterForm(request.GET))
        
    filters_form = MeterFiltersForm(request.GET)
    
    
    meter_queryset = base_context.get("meters", get_meter_queryset(authenticated_user))
    # Apply filters to the queryset
    meter_queryset = MeterListFilter(request.GET, queryset=meter_queryset).qs
    
    paginator = paginate_queryset(meter_queryset, MAX_ITEMS_PER_PAGE)
    page_number = get_page_number(request)
    page = paginator.page(page_number)

    base_context["meters"] = page.object_list

    base_context["paginator"] = paginator
    base_context["page_obj"] = page
  
    base_context["add_meter_form"] = add_meter_form
    base_context["add_meter_category_form"] =  add_meter_category_form
    base_context["search_meter_form"] = search_meter_form
    base_context["filters_form"] = filters_form
    
    return base_context
