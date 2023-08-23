import logging

from django.db import transaction
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import UpdateView, CreateView, FormMixin
from django_filters.views import FilterView

from core.services.notification.backends.exceptions import FailedSMSDeliveryException
from vendor_api.vendors.exceptions import MeterRegistrationException, MeterVendorAPINotFoundException
from users.mixins import AdminOrSuperAdminRequiredMixin

from .filters import MeterFilter
from .forms import MeterCreateForm, MeterRechargeForm, MeterUpdateForm
from .models import Meter
from .decorators import provide_meter_list_template_context

logger = logging.getLogger(__name__)
User = get_user_model()


@provide_meter_list_template_context
class MeterListView(LoginRequiredMixin, FilterView):
    model = Meter
    template_name = "meters/meter_list.html"
    context_object_name = "meters"
    paginate_by = settings.LEGIT_SYSTEMS_MAX_ITEMS_PER_PAGE
    filterset_class = MeterFilter


@provide_meter_list_template_context
class MeterCreateView(LoginRequiredMixin, AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = MeterCreateForm
    template_name = "meters/meter_list.html"
    success_message = "Meter: %(meter_no)s registered successfully"
    success_url = reverse_lazy("meter_list")
    http_method_names = ["post"]

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            meter_no=self.object.meter_number,
        )

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except (MeterVendorAPINotFoundException, MeterRegistrationException) as exc:
            logger.exception("Registration with meter vendor has failed", exc_info=exc)
            messages.error(self.request, "Registration with meter vendor has failed")
        return redirect(self.success_url)

    def form_invalid(self, form):
        return super().render_to_response(self.get_context_data(meter_create_form=form))


@provide_meter_list_template_context
class MeterUpdateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Meter
    form_class = MeterUpdateForm
    template_name = "meters/meter_list.html"
    success_url = reverse_lazy("meter_list")
    success_message = "Changes have been saved"

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except (MeterVendorAPINotFoundException, MeterRegistrationException) as exc:
            logger.exception("Registration with meter vendor has failed", exc_info=exc)
            messages.error(self.request, "Registration with meter vendor has failed")
        return redirect(self.success_url)


@provide_meter_list_template_context
class MeterRechargeView(LoginRequiredMixin, SingleObjectMixin, SuccessMessageMixin, FormMixin, ContextMixin,
                        TemplateResponseMixin, View):
    model = Meter
    template_name = "meters/meter_list.html"
    success_message = "Please wait for the payment prompt to authorize the payment"
    form_class = MeterRechargeForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        meter_recharge_form = self.get_form()
        if meter_recharge_form.is_valid():
            return self.form_valid(meter_recharge_form)
        return self.form_invalid(meter_recharge_form)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())

    @transaction.atomic
    def form_valid(self, form):
        try:
            form.recharge()
        except FailedSMSDeliveryException:
            pass  # Don't revert db changes because an SMS failed to be delivered
        messages.success(self.request, self.get_success_message(cleaned_data={}))
        return self.render_to_response(context=self.get_context_data(meter_recharge_form=form))

    def form_invalid(self, form):
        return self.render_to_response(context=self.get_context_data(meter_recharge_form=form))


class MeterDeactivateView(AdminOrSuperAdminRequiredMixin, SingleObjectMixin, SuccessMessageMixin, View):
    model = Meter
    success_message = "Meter: %(meter_number)s has been deactivated"
    success_url = "meter_list"
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        self.object = meter = self.get_object()
        meter.deactivate()
        messages.success(request, self.get_success_message(cleaned_data={"meter_number": meter.meter_number}))
        return redirect(self.success_url)


class MeterActivateView(AdminOrSuperAdminRequiredMixin, SingleObjectMixin, SuccessMessageMixin, View):
    model = Meter
    success_message = "Meter: %(meter_number)s has been activated"
    success_url = "meter_list"
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        self.object = meter = self.get_object()
        meter.activate()
        messages.success(request, self.get_success_message(cleaned_data={"meter_number": meter.meter_number}))
        return redirect(self.success_url)


class RegisterMeterWithVendorView(AdminOrSuperAdminRequiredMixin, SingleObjectMixin, SuccessMessageMixin, View):
    model = Meter
    success_message = "Meter has been registered"
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        self.object = meter = self.get_object()
        try:
            meter.register()
        except MeterRegistrationException as exc:
            logger.exception("Registration with meter vendor has failed", exc_info=exc)
            messages.error(request, "Registration with meter vendor has failed")
        else:
            messages.success(request, self.get_success_message(cleaned_data={}))
        return redirect("meter_list")

