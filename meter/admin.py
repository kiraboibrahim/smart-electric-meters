from django.contrib import admin
from .models import Meter, TokenHistory


# Register your models here.
admin.site.register(Meter)
admin.site.register(TokenHistory)
