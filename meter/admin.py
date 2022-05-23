from django.contrib import admin
from .models import Meter, TokenHistory, Manufacturer, MeterCategory


# Register your models here.
admin.site.register(Meter)
admin.site.register(TokenHistory)
admin.site.register(Manufacturer)
admin.site.register(MeterCategory)
