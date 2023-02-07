from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect

from shared.auth.mixins import AdminOrSuperAdminRequiredMixin
from shared.views import SearchListView

from manufacturers.models import MeterManufacturer
from manufacturers.forms import AddMeterManufacturerForm, MeterManufacturerSearchForm
from manufacturers.filters import MeterManufacturerSearchUrlQueryKwargMapping


class MeterManufacturerCreateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = MeterManufacturer
    form_class = AddMeterManufacturerForm
    template_name = "manufacturers/list_manufacturers.html.development"
    success_url = reverse_lazy("list_meter_manufacturers")
    success_message = "Meter manufacturer: %(meter_manufacturer_name)s added successfully ."
    
    def get_success_message(self, cleaned_data):
        meter_manufacturer = self.object
        return self.success_message % dict(
            cleaned_data,
            meter_manufacturer_name=meter_manufacturer.name,
        )


class MeterManufacturerListView(AdminOrSuperAdminRequiredMixin, ListView):
    template_name = "manufacturers/list_manufacturers.html.development"
    context_object_name = "meter_manufacturers"
    model = MeterManufacturer
    extra_context = {
        "meter_manufacturer_search_form": MeterManufacturerSearchForm(),
        "add_meter_manufacturer_form": AddMeterManufacturerForm()
    }


class MeterManufacturerEditView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = MeterManufacturer
    fields = "__all__"
    template_name = "manufacturers/edit_manufacturer.html.development"
    extra_context = {
        "meter_manufacturers": MeterManufacturer.objects.all(),
        "meter_manufacturer_search_form": MeterManufacturerSearchForm()
    }
    success_message = "Changes saved successfully."

    def get_success_url(self):
        success_url = reverse_lazy("list_meter_manufacturers")
        return success_url

    def get_context_data(self, **kwargs):
        context = super(MeterManufacturerEditView, self).get_context_data(**kwargs)
        context["edit_meter_manufacturer_form"] = context["form"]
        return context


class MeterManufacturerSearchView(AdminOrSuperAdminRequiredMixin, SearchListView):
    model = MeterManufacturer
    template_name = "manufacturers/list_manufacturers.html.development"
    context_object_name = "meter_manufacturers"
    extra_context = {
        "add_meter_manufacturer_form": AddMeterManufacturerForm()
    }
    search_url_query_kwarg_mapping_class = MeterManufacturerSearchUrlQueryKwargMapping

    def get_context_data(self, **kwargs):
        meter_manufacturer_search_form = MeterManufacturerSearchForm(self.request.GET)
        context = super(MeterManufacturerSearchView, self).get_context_data(**kwargs)
        context["meter_manufacturer_search_form"] = meter_manufacturer_search_form
        return context


class MeterManufacturerDeleteView(AdminOrSuperAdminRequiredMixin, DeleteView):
    model = MeterManufacturer
    success_url = reverse_lazy("list_meter_manufacturers")
    delete_success_message = "Meter manufacturer: %(meter_manufacturer_name)s successfully deleted"
    delete_failure_message = "Meter manufacturer: %(meter_manufacturer_name)s deletion failed. " \
                             "Ensure there are no meters for this manufacturer"
    http_method_names = ["get"]

    def get_object(self):
        if not hasattr(self, "object"):
            self.object = super(MeterManufacturerDeleteView, self).get_object()
        return self.object
            
    def get_delete_failure_message(self):
        meter_manufacturer = self.get_object()
        return self.delete_failure_message % {'meter_manufacturer_name': meter_manufacturer.name}

    def get_delete_success_message(self):
        meter_manufacturer = self.get_object()
        return self.delete_success_message % {'meter_manufacturer_name': meter_manufacturer.name}

    def get(self, request, *args, **kwargs):
        meter_manufacturer_has_meters = self.get_object().meters.exists()
        if not meter_manufacturer_has_meters:
            messages.success(request, self.get_delete_success_message())
            return self.delete(request, *args, **kwargs)
        else:
            messages.error(request, self.get_delete_failure_message())
            return HttpResponseRedirect(self.get_success_url())
