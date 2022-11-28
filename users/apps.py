from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


class UserConfig(AppConfig):
    name = 'users'

    def ready(self):
        from . import signals
        
        from .models import DefaultMeterManager
        from .account_types import MANAGER

        User = get_user_model()
        default_meter_manager, is_created = User.objects.get_or_create(phone_no=settings.DEFAULT_MANAGER_PHONE_NO,
                                                                       first_name=settings.DEFAULT_MANAGER_FIRST_NAME,
                                                                       last_name=settings.DEFAULT_MANAGER_LAST_NAME,
                                                                       address=settings.DEFAULT_MANAGER_ADDRESS,
                                                                       account_type=MANAGER
                                                                      )
        if is_created:
            default_meter_manager.set_unusable_password()
        if DefaultMeterManager.objects.all().count() == 0:
            DefaultMeterManager.objects.create(manager=default_meter_manager)
