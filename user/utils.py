from hashids import Hashids
from django.conf import settings
from django.http import HttpResponse
from user.account_types import SUPER_ADMIN, ADMIN, MANAGER

hashids = Hashids(settings.HASHIDS_SALT, min_length=14)

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


def is_action_allowed(logged_in_user_account_type, target):
    
    if logged_in_user_account_type == ADMIN and (target.account_type == SUPER_ADMIN or target.account_type == ADMIN):
        return False

    if logged_in_user_account_type == SUPER_ADMIN and target.account_type == SUPER_ADMIN:
        return False
    
    return True
