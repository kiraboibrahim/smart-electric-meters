from django.conf import settings

from .models import MeterCategory


def get_default_meter_category():
    return MeterCategory.objects.get(label=settings.DEFAULT_METER_CATEGORY_LABEL)
