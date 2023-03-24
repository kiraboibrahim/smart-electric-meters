from django.conf import settings

from .models import MeterCategory


def get_default_meter_category():
    return MeterCategory.objects.get(label=settings.DEFAULTS["METER_CATEGORY"]["label"])
