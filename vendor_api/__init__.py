from .models import Meter


def register_meter(meter):
    return Meter(meter).register()


def recharge_meter(meter, num_of_units):
    return Meter(meter).recharge(num_of_units)
