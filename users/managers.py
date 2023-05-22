from django.contrib.auth.base_user import BaseUserManager
from django.conf import settings
from django.db.utils import IntegrityError

from users.account_types import DJANGO_SUPERUSER, SUPER_ADMIN, ADMIN, MANAGER, DEFAULT_MANAGER
from shared.decorators import ignore_table_does_not_exist_exception


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
        extra_fields["account_type"] = MANAGER
        user = self.create_user(phone_no, first_name, last_name, address, password, **extra_fields) 
        return user

    def create_admin(self, phone_no, first_name, last_name, address, password=None, **extra_fields):
        extra_fields["account_type"] = ADMIN
        user = self.create_user(phone_no, first_name, last_name, address, password, **extra_fields) 
        return user

    def create_super_admin(self, phone_no, first_name, last_name, address, password=None, **extra_fields):
        extra_fields["account_type"] = SUPER_ADMIN
        user = self.create_user(phone_no, first_name, last_name, address, password, **extra_fields) 
        return user

    def create_superuser(self, phone_no, first_name, last_name, address, password=None, **extra_fields):
        extra_fields["account_type"] = DJANGO_SUPERUSER
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        user = self.create_user(phone_no, first_name, last_name, address, password, **extra_fields) 
        return user

    @ignore_table_does_not_exist_exception
    def create_default_manager(self):
        lookup, defaults = self._get_default_manager_config()
        defaults["account_type"] = DEFAULT_MANAGER
        default_manager, is_created = self.get_or_create(**lookup, defaults=defaults)
        if is_created:
            default_manager.set_unusable_password()
        return default_manager

    @ignore_table_does_not_exist_exception
    def get_default_manager(self):
        lookup, _ = self._get_default_manager_config()
        return self.get(**lookup)

    @staticmethod
    def _get_default_manager_config():
        lookup = {
            settings.DEFAULTS["MANAGER"]["lookup_field"]: settings.DEFAULTS["MANAGER"]["lookup_value"]
        }
        defaults = settings.DEFAULTS["MANAGER"]["defaults"]
        return lookup, defaults
