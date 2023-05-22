from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model

from shared.decorators import ignore_table_does_not_exist_exception


class UserConfig(AppConfig):
    name = 'users'

    def ready(self):
        from . import signals
        from .account_types import DEFAULT_MANAGER
        from .models import UnitPrice

        User = get_user_model()

        @ignore_table_does_not_exist_exception
        def create_default_meter_manager():
            default_manager, is_manager_created = User.objects.get_or_create(**settings.DEFAULTS["MANAGER"],
                                                                             account_type=DEFAULT_MANAGER)
            if is_manager_created:
                default_manager.set_unusable_password()
                UnitPrice.objects.get_or_create(manager=default_manager)
        create_default_meter_manager()
