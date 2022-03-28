from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from .utils import is_admin, is_super_admin

# Create your views here.

# List all meters
@user_passes_test(is_admin_or_super_admin)
def list_meters(request):
    pass
