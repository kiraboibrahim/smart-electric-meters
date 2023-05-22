from django.apps import AppConfig
from django.conf import settings

from shared.decorators import ignore_table_does_not_exist_exception


class MeterCategoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'meter_categories'

    def ready(self):
        from .models import MeterCategory

        @ignore_table_does_not_exist_exception
        def create_default_meter_category():
            MeterCategory.objects.get_or_create(**settings.DEFAULTS["METER_CATEGORY"])

        create_default_meter_category()
