from functools import wraps

from django.conf import settings
from django.core.paginator import Paginator

from .forms import MeterCreateForm, MeterRechargeForm, MeterUpdateForm
from .models import Meter
from .filters import MeterFilter


def provide_meter_list_template_context(cls):
    if type(cls).__name__ == "function":
        raise ValueError("Decorator should be used on only classes, not functions")

    def get_original_get_context_data_fn():
        try:
            fn = cls.get_context_data
        except AttributeError:
            raise AttributeError(f"{cls.__name__} doesn't define get_context_data()")
        return fn

    original_get_context_data_fn = get_original_get_context_data_fn()
    max_items_per_page = settings.LEGIT_SYSTEMS_MAX_ITEMS_PER_PAGE
    first_page = 1

    @wraps(original_get_context_data_fn)
    def get_context_data(self, *args, **kwargs):
        meter_filter = MeterFilter(data=self.request.GET, queryset=Meter.objects.for_user(self.request.user), request=self.request)
        paginator, page, meters, is_paginated = paginate_queryset(meter_filter.qs)
        context = {
            "paginator": paginator,
            "page_obj": page,
            "is_paginated": is_paginated,
            "meters": page.object_list,
            "meter_create_form": MeterCreateForm(),
            "meter_update_form": MeterUpdateForm(),
            "meter_recharge_form": MeterRechargeForm(user=self.request.user),
            "filter": meter_filter
        }
        context.update(original_get_context_data_fn(self, *args, **kwargs))
        return context

    def paginate_queryset(queryset):
        paginator = Paginator(queryset, max_items_per_page)
        page = paginator.page(first_page)
        return paginator, page, page.object_list, page.has_other_pages()

    cls.get_context_data = get_context_data
    return cls
