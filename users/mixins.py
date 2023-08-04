from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin


class AdminOrSuperAdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_admin() or request.user.is_super_admin()):
            return super().dispatch(request, *args, **kwargs)
        messages.error(request, f"You don't have permission to access page: {request.path_info}")
        return self.handle_no_permission()


class ManagerRequiredMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_manager():
            return super().dispatch(request, *args, **kwargs)
        messages.error(request, f"You don't have permission to access page: <span class='fw-bold'>{request.path_info}</span>")
        return self.handle_no_permission()


