from hashids import Hashids
from django.conf import settings
from django.http import HttpResponse
from user.account_types import SUPER_ADMIN, ADMIN, MANAGER

EDIT = 1
DELETE = 2

# Forbidden operations of Administrators and Super Administrators: Format = (caller, callee)
FORBIDDEN_ADMINS_OPS_ON_USER_MODEL = {
    EDIT: [
        (ADMIN, SUPER_ADMIN),
        (ADMIN, ADMIN),
        (SUPER_ADMIN, SUPER_ADMIN),
    ]
}
FORBIDDEN_ADMINS_OPS_ON_USER_MODEL[DELETE] = FORBIDDEN_ADMINS_OPS_ON_USER_MODEL[EDIT] 


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
    

def is_forbidden_user_model_operation(operation):
    operation_type = operation[0]
    operation_caller = operation[1]
    operation_callee = operation[2]
    
    return (operation_caller.account_type, operation_callee.account_type) in FORBIDDEN_ADMINS_OPS_ON_USER_MODEL[opertaion_type]
