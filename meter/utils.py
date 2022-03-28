# These are simple functions that will come in handy in different apps
from user.acc_types import SUPER_ADMIN, ADMIN, MANAGER

def is_admin(user):
    if ((user.acc_type & ADMIN) != 0):
        return True
    return False
    

def is_super_admin(user):
    if ((user.acc_type & SUPER_ADMIN) != 0):
        return True
    return False

def is_admin_or_super_admin(user):
    if is_admin(user) or is_super_admin(user):
        return True
    return False
