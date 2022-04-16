from django.contrib import admin
from .models import Meter, TokenHistory, Manufacturer, MeterType


# Register your models here.
admin.site.register(Meter)
admin.site.register(TokenHistory)
admin.site.register(Manufacturer)
admin.site.register(MeterType)
