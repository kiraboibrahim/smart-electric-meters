# These are simple functions that will come in handy in different apps
from user.acc_types import NONE, SUPER_ADMIN, ADMIN, MANAGER
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    if user.is_authenticated:
        if ((user.acc_type & ADMIN) != 0):
            return True
    return False
    

def is_super_admin(user):
    if user.is_authenticated:
        if ((user.acc_type & SUPER_ADMIN) != 0):
            return True
    return False

def is_admin_or_super_admin(user):
    if user.is_authenticated:
        if is_admin(user) or is_super_admin(user):
            return True
    return False

class SuperAdminRequiredMixin(object):
    @method_decorator(user_passes_test(is_super_admin))
    def dispatch(self, *args, **kwargs):
        return super(SuperAdminRequiredMixin, self).dispatch(*args, **kwargs)


class AdminRequiredMixin(object):
    @method_decorator(user_passes_test(is_admin))
    def dispatch(self, *args, **kwargs):
        return super(AdminRequiredMixin, self).dispatch(*args, **kwargs)

class AdminOrSuperAdminRequiredMixin(object):
    @method_decorator(user_passes_test(is_admin_or_super_admin))
    def dispatch(self, *args, **kwargs):
        return super(AdminOrSuperAdminRequiredMixin, self).dispatch(*args, **kwargs)


def meter_manufacturer_hash(meter_manufacturer):
    return meter_manufacturer.title().strip().replace(" ", "")
    
