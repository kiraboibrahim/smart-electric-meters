import logging

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
from django.views.generic.edit import UpdateView, CreateView

from meter_categories.forms import AddMeterCategoryForm
from payments.models import Payment
from recharge_tokens.models import RechargeToken
from shared.auth.mixins import AdminOrSuperAdminRequiredMixin
from shared.forms import SearchForm as MeterSearchForm
from shared.views import SearchListView, FilterListView
from vendor_api.vendors.exceptions import MeterRegistrationException, EmptyTokenResponseException, \
    MeterVendorAPINotFoundException
from .filters import MeterSearchUrlQueryKwargMapping, AdminMeterListFilter, ManagerMeterListFilter
from .forms import AddMeterForm, ManagerMeterFiltersForm, AdminMeterFiltersForm, RechargeMeterForm
from .mixins import MetersContextMixin
from .models import Meter
from .utils import get_user_meters

logger = logging.getLogger(__name__)
User = get_user_model()


class MeterListView(LoginRequiredMixin, MetersContextMixin, FilterListView):
    model = Meter
    template_name = "meters/list_meters.html.development"
    context_object_name = "meters"
    paginate_by = settings.MAX_ITEMS_PER_PAGE
    extra_context = {
        "add_meter_form": AddMeterForm(),
        "add_meter_category_form": AddMeterCategoryForm()
    }
    model_list_filter_class = AdminMeterListFilter

    def get_template_names(self):
        if self.request.user.is_manager():
            return "managers/meters/list_meters.html.development"
        return self.template_name

    def get_queryset(self):
        meters = get_user_meters(self.request.user, initial_meters=super().get_queryset())
        return meters

    def get_context_data(self, **kwargs):
        context = self.get_meters_context()
        context.update(super().get_context_data(**kwargs))
        context.update({
            "meter_search_form": MeterSearchForm(self.request.GET),
            "filters_form": ManagerMeterFiltersForm(self.request.GET) if self.request.user.is_manager() else
            AdminMeterFiltersForm(self.request.GET),
        })
        return context


class MeterSearchView(LoginRequiredMixin, MetersContextMixin, SearchListView):
    model = Meter
    template_name = "meters/list_meters.html.development"
    context_object_name = "meters"
    extra_context = {
        "add_meter_form": AddMeterForm(),
        "add_meter_category_form": AddMeterCategoryForm()
    }
    paginate_by = settings.MAX_ITEMS_PER_PAGE

    search_url_query_kwarg_mapping_class = MeterSearchUrlQueryKwargMapping
    model_list_filter_class = AdminMeterListFilter

    def get_model_list_filter_class(self):
        if self.request.user.is_manager():
            return ManagerMeterListFilter
        return self.model_list_filter_class

    def get_template_names(self):
        if self.request.user.is_manager():
            return "managers/meters/list_meters.html.development"
        return self.template_name

    def get_queryset(self):
        meters = get_user_meters(self.request.user, initial_meters=super().get_queryset())
        return meters

    def get_context_data(self, **kwargs):
        context = self.get_meters_context()
        context.update(super().get_context_data(**kwargs))
        context.update({
            "filters_form": ManagerMeterFiltersForm(self.request.GET) if self.request.user.is_manager() else
            AdminMeterFiltersForm(self.request.GET),
            "meter_search_form": MeterSearchForm(self.request.GET),
        })
        return context


class MeterCreateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, MetersContextMixin, CreateView):
    form_class = AddMeterForm
    template_name = "meters/list_meters.html.development"
    success_message = "Meter: %(meter_no)s registered successfully"
    success_url = reverse_lazy("list_meters")
    http_method_names = ["post"]
    extra_context = {
        "meter_search_form": MeterSearchForm(),
        "filters_form": AdminMeterFiltersForm(),
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
        context.update(self.get_meters_context())
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
    object = None

    def get_template_names(self):
        if self.request.user.is_manager():
            return "managers/meters/recharge_meter.html.development"
        return self.template_name

    def get(self, request, *args, **kwargs):
        self.object = meter = self.get_object()
        initial_recharge_meter_form_data = {"meter_no": meter.meter_no, "price_per_unit": meter.unit_price}
        recharge_meter_form = RechargeMeterForm(request.user, initial=initial_recharge_meter_form_data)
        context = self.get_context_data(recharge_meter_form=recharge_meter_form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        recharge_meter_form = RechargeMeterForm(request.user, request.POST)
        if recharge_meter_form.is_valid():
            try:
                recharge_token = recharge_meter_form.recharge()
                self.save_recharge_token(recharge_token)
                success_message = self.get_success_message({"token_no": recharge_token.token_no, "num_of_units": recharge_token.num_of_units,"unit": recharge_token.unit})
                messages.success(request, success_message)
            except Exception as exc:
                logger.exception(str(exc))
                messages.error(request, "Something went wrong")
        context = self.get_context_data(recharge_meter_form=recharge_meter_form)
        return self.render_to_response(context=context)

    def save_recharge_token(self, recharge_token):
        payment = Payment(user=self.request.user, amount_paid=recharge_token.amount_paid, charges=recharge_token.charges)
        payment.is_virtual = True
        payment.save()
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
        messages.success(request, self.get_success_message({"meter_no": meter.meter_no}))
        return redirect(self.success_url)

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
        messages.success(request, self.get_success_message({"meter_no": meter.meter_no}))
        return redirect(self.success_url)

    @staticmethod
    def activate_meter(meter):
        meter.activate()
