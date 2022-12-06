from django.conf import settings
from django.core.exceptions import ValidationError


def is_not_default_meter_category(meter_category_label):
    if meter_category_label == settings.DEFAULT_METER_CATEGORY_LABEL:
        raise ValidationError("Cannot modify default meter category")
    return meter_category_label
