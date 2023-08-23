from django.db import models
from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.base_user import BaseUserManager

from core.decorators import ignore_table_does_not_exist_exception

from .account_types import ADMIN, DJANGO_ADMIN, SUPER_ADMIN, MANAGER, DEFAULT_MANAGER


class UserManager(BaseUserManager):
    def create_user(self, phone_no, first_name, last_name, address, password=None,  **extra_fields):
        extra_fields.setdefault("email")
        if extra_fields["email"]:
            extra_fields["email"] = self.normalize_email(extra_fields["email"])
        user = self.model(first_name=first_name, last_name=last_name, phone_no=phone_no, address=address, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_manager(self, phone_no, first_name, last_name, address, password=None, **extra_fields):
        extra_fields.update({
            "account_type": MANAGER
        })
        unit_price = extra_fields.pop("unit_price", settings.LEGIT_SYSTEMS_DEFAULT_UNIT_PRICE)
        user = self.create_user(phone_no, first_name, last_name, address, password=password, **extra_fields)
        from .models import UnitPrice
        UnitPrice.objects.create(manager=user, price=unit_price)
        return user

    def create_admin(self, phone_no, first_name, last_name, address, password=None, **extra_fields):
        extra_fields.update({
            "account_type": ADMIN
        })
        user = self.create_user(phone_no, first_name, last_name, address, password=password, **extra_fields)
        return user

    def create_super_admin(self, phone_no, first_name, last_name, address, password=None, **extra_fields):
        extra_fields.update({
            "account_type": SUPER_ADMIN
        })
        user = self.create_user(phone_no, first_name, last_name, address, password=password, **extra_fields)
        return user

    def create_superuser(self, phone_no, first_name, last_name, address, password=None, **extra_fields):
        extra_fields["account_type"] = DJANGO_ADMIN
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        user = self.create_user(phone_no, first_name, last_name, address, password=password, **extra_fields)
        return user

    @method_decorator(ignore_table_does_not_exist_exception)
    def create_default_manager(self):
        filters, defaults = self._get_default_manager_config()
        self.filter(account_type=DEFAULT_MANAGER).exclude(**filters).delete()
        default_manager, is_created = self.get_or_create(**filters, defaults=defaults)
        if is_created:
            default_manager.set_unusable_password()
            from .models import UnitPrice
            UnitPrice.objects.create(manager=default_manager, price=settings.LEGIT_SYSTEMS_DEFAULT_UNIT_PRICE)
        return default_manager

    @method_decorator(ignore_table_does_not_exist_exception)
    def get_default_manager(self):
        filters, _ = self._get_default_manager_config()
        return self.get(**filters)

    @staticmethod
    def _get_default_manager_config():
        filters = {
            settings.LEGIT_SYSTEMS_DEFAULT_MANAGER["MANAGER"]["lookup_field"]: settings.LEGIT_SYSTEMS_DEFAULT_MANAGER["MANAGER"]["lookup_value"]
        }
        defaults = settings.LEGIT_SYSTEMS_DEFAULT_MANAGER["MANAGER"]["defaults"]
        defaults["account_type"] = DEFAULT_MANAGER
        return filters, defaults

    def all_managers(self):
        return self.all().filter(models.Q(account_type=MANAGER) | models.Q(account_type=DEFAULT_MANAGER))
