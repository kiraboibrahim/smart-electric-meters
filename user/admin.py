from django.contrib import admin
from user.models import PrepaidMeterUser, UnitPrice
from django.contrib.auth.admin import UserAdmin
# Register your models here.

admin.site.register(UnitPrice)
admin.site.register(PrepaidMeterUser)
