from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

from meter.utils import is_admin, is_super_admin, is_admin_or_super_admin, SuperAdminRequiredMixin, AdminRequiredMixin, AdminOrSuperAdminRequiredMixin
from meter.models import MeterCategory, Meter


# Create your views here.
User = get_user_model()


class MeterListView(AdminOrSuperAdminRequiredMixin, ListView):
    template_name = "meter/list_meters.html.development"
    context_object_name = "meters"
    model = Meter

    
class MeterCreateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Meter
    template_name = "meter/create_meter.html.development"
    fields = "__all__"
    success_url = reverse_lazy("register_meter")
    success_message = "Meter: %(meter_no)s registered successfully."
    
    def get_success_message(self, cleaned_data):
        # Make the meter number accessible in the success_message
        return self.success_message % dict(
            cleaned_data,
            meter_no=self.object.meter_no,
        )
    
    """ TODO: Initialize manager field with only managers """
    """ TODO: Register remotely with the company manufacturer API """
    

    
class MeterEditView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Meter
    template_name = "meter/edit_meter.html.development"
    fields = "__all__"
    success_message = "Changes saved successfully."

    def get_success_url(self):
        url = reverse_lazy("edit_meter", kwarrgs={"pk":self.object.id})
        return url
    
class MeterCategoryCreateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = MeterCategory
    template_name = "meter/register_meter_category.html.development"
    fields = "__all__"
    success_url = reverse_lazy("register_meter_category") # change this
    success_message = "Meter Category: %(label)s registered successfully."
    
    def get_success_message(self, cleaned_data):
        # Make the meter number accessible in the success_message
        return self.success_message % dict(
            cleaned_data
        ) 
    
@user_passes_test(is_admin_or_super_admin)
def delete_meter(request, pk):
    meter = get_object_or_404(Meter, pk=pk)
    meter.delete()
    messages.success(request, "Meter: %s has been deleted successfully." %(meter.meter_no))
    return redirect("list_meters")

def buy_token(request, pk):
    # This view will not require authentication
    return HttpResponse(response %("generate token"))

def unlink_meter(request, pk):
    meter = get_object_or_404(Meter, pk=pk)
    # Unlink the meter from the manager it was assigned
    meter.manager = None
    meter.save()
    messages.success(request, "Meter %s has been unlinked successfully" %(meter.meter_no))
    return redirect("list_meters")

