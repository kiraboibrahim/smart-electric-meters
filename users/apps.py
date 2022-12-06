from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model


class UserConfig(AppConfig):
    name = 'users'

    def ready(self):
        from . import signals

        from .account_types import DEFAULT_MANAGER

        User = get_user_model()
        default_meter_manager, is_created = User.objects.get_or_create(phone_no=settings.DEFAULT_MANAGER_PHONE_NO,
                                                                       first_name=settings.DEFAULT_MANAGER_FIRST_NAME,
                                                                       last_name=settings.DEFAULT_MANAGER_LAST_NAME,
                                                                       address=settings.DEFAULT_MANAGER_ADDRESS,
                                                                       account_type=DEFAULT_MANAGER
                                                                       )
        if is_created:
            default_meter_manager.set_unusable_password()
