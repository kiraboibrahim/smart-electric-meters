from django.contrib import admin
from .models import PrepaidMeterUser, PricePerUnit
from django.contrib.auth.admin import UserAdmin
# Register your models here.

admin.site.register(PrepaidMeterUser, UserAdmin)
admin.site.register(PricePerUnit)
