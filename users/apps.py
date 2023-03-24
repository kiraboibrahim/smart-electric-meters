from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model


class UserConfig(AppConfig):
    name = 'users'

    def ready(self):
        from . import signals
        from .account_types import DEFAULT_MANAGER
        from .models import UnitPrice

        User = get_user_model()
        default_manager, is_manager_created = User.objects.get_or_create(**settings.DEFAULTS["MANAGER"], account_type=DEFAULT_MANAGER)
        if is_manager_created:
            default_manager.set_unusable_password()
            UnitPrice.objects.get_or_create(manager=default_manager)
