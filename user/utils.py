from hashids import Hashids
from django.conf import settings
from django.http import HttpResponse
from user.acc_types import SUPER_ADMIN, ADMIN, MANAGER

hashids = Hashids(settings.HASHIDS_SALT, min_length=8)

def h_encode(id):
    return hashids.encode(id)

def h_decode(h):
    z = hashids.decode(h)
    if z:
        return z[0]


class HashIdConverter:
    regex = "[a-zA-Z0-9]{8,}"

    def to_python(self, value):
        return h_decode(value)

    def to_url(self, value):
        return h_encode(value)

def allow_or_deny_action(logged_in_user_acc_type, target):
    
    if logged_in_user_acc_type == ADMIN and (target.acc_type == SUPER_ADMIN or target.acc_type == ADMIN):
        return HttpResponse("Action not allowed", status=403)

    if logged_in_user_acc_type == SUPER_ADMIN and target.acc_type == SUPER_ADMIN:
        return HttpResponse("Action not allowed", status=403)
