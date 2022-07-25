from hashids import Hashids
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth import get_user_model


from user.account_types import SUPER_ADMIN, ADMIN, MANAGER
from user.forms import AdminCreateUserForm, SuperAdminCreateUserForm


class ModelOperations:
    EDIT = 1
    DELETE = 2

# Forbidden operations of Administrators and Super Administrators: Format = (caller, callee)
FORBIDDEN_ADMINS_OPS_ON_USER_MODEL = {
    ModelOperations.EDIT: [
        (ADMIN, SUPER_ADMIN),
        (ADMIN, ADMIN),
        (SUPER_ADMIN, SUPER_ADMIN),
    ]
}
FORBIDDEN_ADMINS_OPS_ON_USER_MODEL[ModelOperations.DELETE] = FORBIDDEN_ADMINS_OPS_ON_USER_MODEL[ModelOperations.EDIT] 


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
    
    return (operation_caller.account_type, operation_callee.account_type) in FORBIDDEN_ADMINS_OPS_ON_USER_MODEL[operation_type]


def get_users(logged_in_user):
    User = get_user_model()
    users = None
    
    logged_in_user_account_type = logged_in_user.account_type
    if logged_in_user_account_type == SUPER_ADMIN:
        users = User.objects.filter(Q(account_type=MANAGER) | Q(account_type=ADMIN))
    else:
        users= User.objects.filter(Q(account_type=MANAGER))

    return users

def get_add_user_form_class(logged_in_user):
    form_class = None
    
    if logged_in_user.account_type == SUPER_ADMIN:
        form_class = SuperAdminCreateUserForm
    else:
        form_class = AdminCreateUserForm
        
    return form_class
