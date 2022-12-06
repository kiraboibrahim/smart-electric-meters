from .models import Meter


def get_user_meters(user, initial_meters=None):
    meters = initial_meters if initial_meters is not None else Meter.objects.all()
    if user.is_manager():
        meters = meters.filter(manager=user)
    return meters
