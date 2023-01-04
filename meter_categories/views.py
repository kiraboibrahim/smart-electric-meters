from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from shared.auth.mixins import AdminOrSuperAdminRequiredMixin
from shared.forms import SearchForm as MeterSearchForm

from meter_categories.models import MeterCategory

from meters.forms import AddMeterForm, AdminMeterFiltersForm
from meters.mixins import MetersContextMixin


class MeterCategoryCreateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, MetersContextMixin, CreateView):
    model = MeterCategory
    template_name = "meters/list_meters.html.development"
    fields = "__all__"
    success_url = reverse_lazy("list_meters")
    success_message = "Meter category: %(label)s added"
    extra_context = {
        "meter_search_form": MeterSearchForm(),
        "filters_form": AdminMeterFiltersForm(),
        "add_meter_form": AddMeterForm(),
    }
    
    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data)

    def get_context_data(self, **kwargs):
        context = super(MeterCategoryCreateView, self).get_context_data(**kwargs)
        context.update(self.get_meters_context(self.request.user))
        context["add_meter_category_form"] = context.get("form")
        return context
