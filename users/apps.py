from django.apps import AppConfig
from django.contrib.auth import get_user_model


class UserConfig(AppConfig):
    name = 'users'

    def ready(self):
        from . import signals

        User = get_user_model()
        User.objects.create_default_manager()

