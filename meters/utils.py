from .models import Meter


def get_user_meters(user):
    meters = Meter.objects.all()
    if user.is_manager():
        meters = meters.filter(manager=user)
    return meters
