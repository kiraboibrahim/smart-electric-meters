from django.apps import AppConfig
from django.conf import settings


class MeterCategoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'meter_categories'

    def ready(self):
        from .models import MeterCategory

        """MeterCategory.objects.get_or_create(**settings.DEFAULTS["METER_CATEGORY"])"""
