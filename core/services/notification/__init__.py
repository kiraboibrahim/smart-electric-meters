import logging

from django.conf import settings
from django.utils.module_loading import import_string

from .strategies import BY_SMS, BY_EMAIL

logger = logging.getLogger(__name__)


def send_notification(to: list[str], subject: str, message: str, notification_strategy=BY_EMAIL):
    if notification_strategy is BY_EMAIL:
        notification_backend = import_string(f"{settings.LEGIT_SYSTEMS_EMAIL_NOTIFICATION_BACKEND}")()
    elif notification_strategy is BY_SMS:
        notification_backend = import_string(f"{settings.LEGIT_SYSTEMS_SMS_NOTIFICATION_BACKEND}")()
    else:
        raise ValueError("Unknown notification strategy")
    return notification_backend.send(to, subject, message)
