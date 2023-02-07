from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model


class UserConfig(AppConfig):
    name = 'users'

    def ready(self):
        from .account_types import DEFAULT_MANAGER
        from .models import UnitPrice

        User = get_user_model()
        default_meter_manager, is_manager_created = User.objects.get_or_create(
            phone_no=settings.DEFAULT_MANAGER_PHONE_NO,
            first_name=settings.DEFAULT_MANAGER_FIRST_NAME,
            last_name=settings.DEFAULT_MANAGER_LAST_NAME,
            address=settings.DEFAULT_MANAGER_ADDRESS,
            account_type=DEFAULT_MANAGER
            )
        if is_manager_created:
            default_meter_manager.set_unusable_password()
            UnitPrice.objects.get_or_create(manager=default_meter_manager)
