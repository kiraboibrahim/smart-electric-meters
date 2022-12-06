from django.apps import AppConfig
from django.conf import settings


class MeterCategoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'meter_categories'

    def ready(self):
        from .models import MeterCategory

        MeterCategory.objects.get_or_create(
            percentage_charge=settings.DEFAULT_METER_CATEGORY_PERCENTAGE_CHARGE,
            fixed_charge=settings.DEFAULT_METER_CATEGORY_FIXED_CHARGE,
            label=settings.DEFAULT_METER_CATEGORY_LABEL
        )
