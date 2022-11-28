from django.conf import settings

from users.models import DefaultMeterManager

from .models import Meter


def get_user_meters(user, initial_meters=None):
    meters = initial_meters if initial_meters is not None else Meter.objects.all()
    if user.is_manager():
        meters = meters.filter(manager=user)
    return meters


def get_default_meter_manager():
    default_meter_manager = DefaultMeterManager.objects.get(manager__phone_no=settings.DEFAULT_MANAGER_PHONE_NO)
    return default_meter_manager.manager
