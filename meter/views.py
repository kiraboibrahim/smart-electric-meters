from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views import View

from search_views.filters import build_q

from prepaid_meters_token_generator_system.auth.mixins import AdminOrSuperAdminRequiredMixin
from prepaid_meters_token_generator_system.views.mixins import SearchMixin
from prepaid_meters_token_generator_system.auth.user_identity_tests import is_admin_or_super_admin
from prepaid_meters_token_generator_system.forms import SearchForm

from meter.utils import get_list_meters_template_context_data, apply_user_filters
from meter.forms import AddMeterForm, RechargeMeterForm
from meter.models import Meter
from meter.filters import MeterSearchFilter

from external_api.vendor.exceptions import MeterRegistrationException, EmptyTokenResponseException, \
    MeterVendorAPINotFoundException
User = get_user_model()


class BaseMeterListView(ListView):
    template_name = "meter/list_meters.html.development"
    context_object_name = "meters"
    model = Meter

    def get_context_data(self, **kwargs):
        base_context = super(BaseMeterListView, self).get_context_data(**kwargs)
        return get_list_meters_template_context_data(self.request, base_context)


class MeterListView(LoginRequiredMixin, BaseMeterListView):
    pass


class MeterSearchView(LoginRequiredMixin, SearchMixin, BaseMeterListView):
    template_name = "meter/search_meters.html.development"
    http_method_names = ["get"]
    search_filters_class = MeterSearchFilter

    def get_queryset(self):
        meters = super(MeterSearchView, self).get_queryset()
        search_filters = self.get_search_filters()
        return meters.filter(search_filters)


class MeterCreateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = AddMeterForm
    template_name = "meter/list_meters.html.development"
    success_message = "Meter: %(meter_no)s registered successfully."
    success_url = reverse_lazy("list_meters")
    http_method_names = ["post"]
    
    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            meter_no=self.object.meter_no,
        )

    def get_context_data(self, **kwargs):
        base_context = super(MeterCreateView, self).get_context_data(**kwargs)
        context = get_list_meters_template_context_data(self.request, base_context)
        return context
    
    def form_valid(self, form):
        # Remove the is_registered field from form data because it is unknown to the meter model
        is_meter_already_remotely_registered = form.cleaned_data.pop("is_registered")
        meter = Meter(**form.cleaned_data)

        try:
            if not is_meter_already_remotely_registered:
                meter.register()
        except MeterRegistrationException:
            messages.error(self.request, "Registration with the meter manufacturer has failed")
            return super(MeterCreateView, self).form_invalid(form)
        
        return super(MeterCreateView, self).form_valid(form)

    
class MeterEditView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Meter
    fields = "__all__"
    template_name = "meter/edit_meter.html.development"
    success_message = "Changes saved successfully."

    def get_success_url(self):
        return reverse_lazy("edit_meter", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        context = super(MeterEditView, self).get_context_data(**kwargs)
        context["meters"] = apply_user_filters(self.request.user, Meter.objects.all())
        return context
    

class RechargeMeterView(View):
    def get(self, request, *args, **kwargs):
        meter_id = kwargs.get("pk")
        meter = get_object_or_404(Meter, pk=meter_id)
        recharge_meter_form = RechargeMeterForm(initial={"meter_no": meter.meter_no})
        context = {
            "recharge_meter_form": recharge_meter_form,
            "meters": apply_user_filters(request.user, Meter.objects.all()),
            "meter_search_form": SearchForm(),
        }
        return render(request, "meter/recharge_meter.html.development", context)
    
    def post(self, request, *args, **kwargs):
        recharge_meter_form = RechargeMeterForm(request.POST)
        if recharge_meter_form.is_valid():
            meter = recharge_meter_form.cleaned_data.pop("meter")
            amount = recharge_meter_form.cleaned_data["amount"]
            meter_manufacturer = meter.manufacturer_name
            try:
                token = meter.get_token(amount)
                """ TODO: Send SMS to user with token number """
                messages.success(request, "Token: %s Units: %s %s" % (token.token_no, token.num_of_units, token.unit))
            except MeterVendorAPINotFoundException:
                error_msg = "The %s API has not been developed yet. Please contact the developer" % meter_manufacturer
                messages.error(request, error_msg)
            except EmptyTokenResponseException:
                error_msg = "No token received. Contact %s's customer helpline or support" % meter_manufacturer
                messages.error(request, error_msg)
            except Exception as e:
                error_msg = "Unknown error"
                messages.error(request, error_msg)

        context = {
            "recharge_meter_form": recharge_meter_form,
            "meters": apply_user_filters(request.user, Meter.objects.all()),
            "meter_search_form": SearchForm(),
        }
        return render(request, "meter/recharge_meter.html.development", context)


@user_passes_test(is_admin_or_super_admin)
def deactivate_meter(request, pk):
    meter = get_object_or_404(Meter, pk=pk)
    meter.is_active = False
    meter.save()
    
    messages.success(request, "Meter: %s has been deleted successfully" % meter.meter_no)
    return redirect("list_meters")
