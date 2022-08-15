import meter.models as meter_models
import meter.forms as meter_forms

from user.account_types import MANAGER


def get_meter_manufacturer_hash(manufacturer_name):
    return manufacturer_name.title().strip().replace(" ", "")


def get_meters(request):
    queryset = meter_models.Meter.objects.all()
    if request.user.account_type == MANAGER:
        queryset = queryset.filter(manager=request.user.id)
        
    return queryset


def get_list_meters_template_context_data(request, base_context={}):
    # The list_meters templates needs the following objects
    add_meter_form = meter_forms.AddMeterForm()
    add_meter_category_form = meter_forms.AddMeterCategoryForm()
    search_form = meter_forms.SearchForm()
    meters = get_meters(request)
        
    base_context.setdefault("add_meter_form", add_meter_form)
    base_context.setdefault("add_meter_category_form", add_meter_category_form)
    base_context.setdefault("search_form", search_form)
    base_context.setdefault("meters", meters)
        
    return base_context
