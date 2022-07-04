from user.account_types import NONE, SUPER_ADMIN, ADMIN, MANAGER


def is_admin(user):
    if user.is_authenticated:
        if ((user.account_type & ADMIN) != 0):
            return True
    return False
    

def is_super_admin(user):
    if user.is_authenticated:
        if ((user.account_type & SUPER_ADMIN) != 0):
            return True
    return False


def is_admin_or_super_admin(user):
    if user.is_authenticated:
        if is_admin(user) or is_super_admin(user):
            return True
    return False
