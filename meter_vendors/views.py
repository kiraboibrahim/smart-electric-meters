from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django_filters.views import FilterView

from users.mixins import AdminOrSuperAdminRequiredMixin

from .filters import MeterVendorFilter
from .forms import MeterVendorCreateForm, MeterVendorUpdateForm
from .models import MeterVendor
from .decorators import provide_meter_vendor_list_template_context


@provide_meter_vendor_list_template_context
class MeterVendorCreateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = MeterVendor
    form_class = MeterVendorCreateForm
    template_name = "meter_vendors/meter_vendor_list.html"
    success_url = reverse_lazy("meter_vendor_list")
    success_message = "Meter vendor: %(meter_vendor_name)s has been added"

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, meter_vendor_name=self.object.name)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(meter_vendor_create_form=form))


@provide_meter_vendor_list_template_context
class MeterVendorListView(AdminOrSuperAdminRequiredMixin, FilterView):
    template_name = "meter_vendors/meter_vendor_list.html"
    context_object_name = "meter_vendors"
    model = MeterVendor
    filterset_class = MeterVendorFilter


@provide_meter_vendor_list_template_context
class MeterVendorUpdateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = MeterVendor
    form_class = MeterVendorUpdateForm
    template_name = "meter_vendors/meter_vendor_list.html"
    success_message = "Changes saved"
    success_url = reverse_lazy("meter_vendor_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meter_vendor_update_form"] = context["form"]
        return context


class MeterVendorDeleteView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, DeleteView):
    model = MeterVendor
    success_url = reverse_lazy("meter_vendor_list")
    success_message = "Meter vendor: %(meter_vendor_name)s has been deleted"
    failure_message = "Meter vendor: %(meter_vendor_name)s deletion failed. " \
                      "Ensure there aren't any meters for this manufacturer"
    http_method_names = ["get"]

    def get_failure_message(self):
        return self.failure_message % {'meter_vendor_name': self.object.name}

    def get_success_message(self, cleaned_data=None):
        return super().get_success_message(cleaned_data={'meter_vendor_name': self.object.name})

    def get(self, request, *args, **kwargs):
        self.object = meter_vendor = self.get_object()
        if meter_vendor.has_meters():
            messages.error(request, self.get_failure_message())
            return HttpResponseRedirect(self.get_success_url())
        messages.success(request, self.get_success_message())
        return self.delete(request, *args, **kwargs)
