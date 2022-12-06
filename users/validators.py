from django.conf import settings
from django.core.exceptions import ValidationError


def is_not_default_manager(phone_no):
    if phone_no == settings.DEFAULT_MANAGER_PHONE_NO:
        raise ValidationError("Default manager cannot be edited")
    return phone_no
