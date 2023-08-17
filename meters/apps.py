from django.apps import AppConfig


class MeterConfig(AppConfig):
    name = 'meters'

    def ready(self):
        from . import signals

