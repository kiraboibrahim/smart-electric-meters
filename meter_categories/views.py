from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from shared.forms import SearchForm as MeterSearchForm
from shared.auth.mixins import AdminOrSuperAdminRequiredMixin

from meter_categories.models import MeterCategory

from meters.mixins import MetersContextMixin
from meters.forms import AddMeterForm, AdminMeterFiltersForm


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


class MeterCategoryEditView(AdminOrSuperAdminRequiredMixin, UpdateView, SuccessMessageMixin):
    model = MeterCategory
    fields = "__all__"
    pk_url_kwarg = "meter_category_id"
    success_url = reverse_lazy("list_meters")
    success_message = "Meter category %(label) updated"
    template_name = "meter_categories/edit_meter_category.html.development"


class MeterCategoryDeleteView(AdminOrSuperAdminRequiredMixin, SingleObjectMixin, SuccessMessageMixin, View):
    model = MeterCategory
    pk_url_kwarg = "meter_category_id"
    http_method_names = ["get"]
    failure_message = "Can't delete category because they are still meters associated to the category"
    success_message = "Meter category deleted"

    def get(self, request, *args, **kwargs):
        meter_category = self.get_object()
        if meter_category.has_meters():
            messages.error(request, self.failure_message)
        else:
            meter_category.delete()
            messages.success(request, self.get_success_message())
        return redirect(reverse_lazy("list_meters"))