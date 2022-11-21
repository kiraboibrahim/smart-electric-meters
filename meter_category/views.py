from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from prepaid_meters_token_generator_system.auth.mixins import AdminOrSuperAdminRequiredMixin

from meter_category.models import MeterCategory

from meter.forms import AddMeterForm
from meter.models import Meter
from meter.utils import apply_user_filters


class MeterCategoryCreateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = MeterCategory
    template_name = "meter/list_meters.html.development"
    fields = "__all__"
    success_url = reverse_lazy("list_meters")
    success_message = "Meter category: %(label)s added successfully"
    
    def get_success_message(self, cleaned_data):
        # Make meter fields accessible to the success_message 
        return self.success_message % dict(cleaned_data)

    def get_context_data(self, **kwargs):
        logged_in_user = self.request.user
        context = super(MeterCategoryCreateView, self).get_context_data(**kwargs)
        
        add_meter_form = AddMeterForm()
        context["add_meter_category_form"] = context["form"]
        context["add_meter_form"] = add_meter_form
        
        context["meters"] = apply_user_filters(self.request.user, Meter.objects.all())

        return context
