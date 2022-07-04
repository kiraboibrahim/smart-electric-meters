from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator

from prepaid_meters_token_generator_system.user_permission_tests import is_admin, is_super_admin, is_admin_or_super_admin


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
