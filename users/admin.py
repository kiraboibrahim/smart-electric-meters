from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from .models import UnitPrice

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    model = User
    ordering = ["-date_joined"]

    
admin.site.register(UnitPrice)
admin.site.register(User)
