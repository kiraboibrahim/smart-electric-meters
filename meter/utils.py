from meter.models import Meter
from user.account_types import MANAGER

def get_meter_manufacturer_hash(manufacturer_name):
    return manufacturer_name.title().strip().replace(" ", "")


def get_meters(request):
    queryset = Meter.objects.all()
    if request.user.account_type == MANAGER:
        queryset = queryset.filter(manager=request.user.id)
        
    return queryset
