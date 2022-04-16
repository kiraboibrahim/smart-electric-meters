from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from .utils import is_admin, is_super_admin, is_admin_or_super_admin
from .models import Meter
from .forms import CreateMeterForm

# Create your views here.

response = "<h1>Hello from %s route</h1>"
User = get_user_model()
# List all meters
@user_passes_test(is_admin_or_super_admin)
def list_meters(request):
    return HttpResponse(response %("list meters"))

#@user_passes_test(is_admin_or_super_admin)
def create_meter(request):
    context = {}
    
    if request.method == 'POST':
        form = CreateMeterForm(request.POST)
        if form.is_valid():
            context["form"] = form
            #form.save()
            # Meter added successfully
            messages.success(request, "Meter: %s has been added successfully." %(form.cleaned_data.get("meter_no")))
        else:
            # Form is invalid
            messages.error(request, "Fix errors in the form.")
    else:
        form = CreateMeterForm()
        context["form"] = form
        
    return render(request, "meter/create_meter.html.development", context)

@user_passes_test(is_admin_or_super_admin)
def edit_meter(request, pk):
    # Edit meter no, manufacture and manufacturer, and Owner
    return HttpResponse(response %("edit meter"))

@user_passes_test(is_admin_or_super_admin)
def delete_meter(request, pk):
    # This is a dangerous view, I myself I don't see the reason why a company would want to delete a meter that is
    # already in production, but anyway, It was specified in the app expected features, So just go on 
    return HttpResponse(response %("delete meter"))

def get_token(request, pk):
    # This view will not require authentication
    return HttpResponse(response %("generate token"))
