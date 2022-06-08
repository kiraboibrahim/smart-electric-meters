from django.contrib import admin
from meter.models import Meter, TokenLog, Manufacturer, MeterCategory


# Register your models here.
admin.site.register(Meter)
admin.site.register(TokenLog)
admin.site.register(Manufacturer)
admin.site.register(MeterCategory)
