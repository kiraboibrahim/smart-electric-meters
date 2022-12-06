import logging

from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.conf import settings
from django.views import View

from shared.auth.mixins import AdminOrSuperAdminRequiredMixin
from shared.views import SearchListView, FilterListView
from shared.forms import SearchForm as MeterSearchForm

from meter_categories.forms import AddMeterCategoryForm

from recharge_tokens.models import RechargeToken

from external_api.vendor.exceptions import MeterRegistrationException, EmptyTokenResponseException, \
    MeterVendorAPINotFoundException

from .models import Meter
from .filters import MeterSearchQueryParameterMapping, MeterFieldsFilter
from .forms import AddMeterForm, MeterFiltersForm, RechargeMeterForm
from .mixins import MetersContextMixin
from .utils import get_user_meters

logger = logging.getLogger(__name__)
User = get_user_model()


class MeterListView(LoginRequiredMixin, FilterListView):
    model = Meter
    template_name = "meters/list_meters.html.development"
    context_object_name = "meters"
    paginate_by = settings.MAX_ITEMS_PER_PAGE
    extra_context = {
        "add_meter_form": AddMeterForm(),
        "add_meter_category_form": AddMeterCategoryForm()
    }
    model_fields_filter_class = MeterFieldsFilter

    def get_queryset(self):
        meters = super().get_queryset()
        meters = get_user_meters(self.request.user, initial_meters=meters)
        return meters

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filters_form"] = MeterFiltersForm(self.request.GET)
        context["meter_search_form"] = MeterSearchForm(self.request.GET)
        return context


class MeterSearchView(LoginRequiredMixin, SearchListView):
    model = Meter
    template_name = "meters/search_meters.html.development"
    context_object_name = "meters"
    extra_context = {
        "add_meter_form": AddMeterForm(),
        "add_meter_category_form": AddMeterCategoryForm()
    }
    paginate_by = settings.MAX_ITEMS_PER_PAGE
    search_query_parameter_mapping_class = MeterSearchQueryParameterMapping
    model_fields_filter_class = MeterFieldsFilter

    def get_queryset(self):
        meters = super().get_queryset()
        meters = get_user_meters(self.request.user, initial_meters=meters)
        return meters

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filters_form"] = MeterFiltersForm(self.request.GET)
        context["meter_search_form"] = MeterSearchForm(self.request.GET)
        return context


class MeterCreateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, MetersContextMixin, CreateView):
    form_class = AddMeterForm
    template_name = "meters/list_meters.html.development"
    success_message = "Meter: %(meter_no)s registered successfully"
    success_url = reverse_lazy("list_meters")
    http_method_names = ["post"]
    extra_context = {
        "meter_search_form": MeterSearchForm(),
        "filters_form": MeterFiltersForm(),
        "add_meter_category_form": AddMeterCategoryForm()
    }

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            meter_no=self.object.meter_no,
        )

    def form_valid(self, form):
        previously_registered_with_manufacturer = form.cleaned_data.pop("is_registered")
        meter = Meter(**form.cleaned_data)
        try:
            if not previously_registered_with_manufacturer:
                meter.register()
        except MeterRegistrationException:
            logger.exception("Meter registration failed")
            messages.error(self.request, "Registration with the meter manufacturer has failed")
            return super(MeterCreateView, self).form_invalid(form)

        return super(MeterCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["add_meter_form"] = context["form"]
        context.update(self.get_meters_context(self.request.user))
        return context


class MeterEditView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Meter
    fields = ("meter_no", "manufacturer", "manager", "category")
    template_name = "meters/edit_meter.html.development"
    success_message = "Changes saved"

    def get_success_url(self):
        return reverse_lazy("edit_meter", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        context = super(MeterEditView, self).get_context_data(**kwargs)
        context["recent_recharge_tokens"] = RechargeToken.get_recent_recharge_tokens_for_meter(self.object)
        return context


class RechargeMeterView(LoginRequiredMixin, SingleObjectMixin, SuccessMessageMixin, ContextMixin, TemplateResponseMixin,
                        View):
    model = Meter
    template_name = "meters/recharge_meter.html.development"
    extra_context = {
        "meter_search_form": MeterSearchForm()
    }
    success_message = "Token: %(token_no)s Units: %(num_of_units)s%(unit)s"
    error_message = None
    object = None

    def get(self, request, *args, **kwargs):
        self.object = meter = self.get_object()
        recharge_meter_form = RechargeMeterForm(request.user, initial={"meter_no": meter.meter_no,
                                                                       "price_per_unit": meter.unit_price
                                                                       }
                                                )
        context = self.get_context_data(recharge_meter_form=recharge_meter_form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        recharge_meter_form = RechargeMeterForm(request.user, request.POST)
        if recharge_meter_form.is_valid():
            meter_manufacturer_name = recharge_meter_form.meter.manufacturer_name
            try:
                recharge_token = recharge_meter_form.recharge(is_manager=request.user.is_manager())
                self.save_recharge_token(recharge_token)
                success_message = self.get_success_message({"token_no": recharge_token.token_no,
                                                            "num_of_units": recharge_token.num_of_units,
                                                            "unit": recharge_token.unit
                                                            })
                messages.success(request, success_message)
            except MeterVendorAPINotFoundException:
                self.error_message = "The %s API has not been developed yet. Please contact the developer" % \
                                     meter_manufacturer_name
            except EmptyTokenResponseException:
                self.error_message = "No token received. Contact %s's customer helpline or support" % \
                                     meter_manufacturer_name
            except Exception:
                logger.exception("Recharge token generation failed")
                self.error_message = "Unknown error"
            if self.error_message:
                messages.error(request, self.error_message)

        context = self.get_context_data(recharge_meter_form=recharge_meter_form)
        return self.render_to_response(context=context)

    @staticmethod
    def save_recharge_token(recharge_token, payment=None):
        RechargeToken.objects.create(token_no=recharge_token.token_no, num_of_units=recharge_token.num_of_units,
                                     meter=recharge_token.meter, payment=payment)


class DeactivateMeterView(AdminOrSuperAdminRequiredMixin, SingleObjectMixin, SuccessMessageMixin, View):
    model = Meter
    success_message = "Meter: %(meter_no)s has been deactivated"
    success_url = "list_meters"
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        meter = self.get_object()
        self.deactivate_meter(meter)
        self.add_success_message(meter_no=meter.meter_no)
        return redirect(self.success_url)

    def add_success_message(self, **kwargs):
        success_message = self.get_success_message(cleaned_data=kwargs)
        messages.success(self.request, success_message)

    @staticmethod
    def deactivate_meter(meter):
        meter.deactivate()


class ActivateMeterView(AdminOrSuperAdminRequiredMixin, SingleObjectMixin, SuccessMessageMixin, View):
    model = Meter
    success_message = "Meter: %(meter_no)s has been activated"
    success_url = "list_meters"
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        meter = self.get_object()
        self.activate_meter(meter)
        self.add_success_message(meter_no=meter.meter_no)
        return redirect(self.success_url)

    def add_success_message(self, **kwargs):
        success_message = self.get_success_message(cleaned_data=kwargs)
        messages.success(self.request, success_message)

    @staticmethod
    def activate_meter(meter):
        meter.activate()
