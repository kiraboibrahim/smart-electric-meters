from functools import wraps

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

from .forms import UserUpdateForm, ManagerCreateForm, AdminCreateForm, SetPasswordForm
from .filters import UserFilter

def provide_user_list_template_context(cls):

    def get_original_get_context_data_fn():
        try:
            fn = cls.get_context_data
        except AttributeError:
            raise AttributeError(f"{cls.__name__} doesn't define get_context_data()")
        return fn

    original_get_context_data_fn = get_original_get_context_data_fn()
    max_items_per_page = settings.LEGIT_SYSTEMS_MAX_ITEMS_PER_PAGE
    first_page = 1

    @wraps(original_get_context_data_fn)
    def get_context_data(self, *args, **kwargs):
        User = get_user_model()
        user_filter = UserFilter(data=self.request.GET, queryset=User.objects.for_user(self.request.user), request=self.request)
        paginator, page, meter_vendors, is_paginated = paginate_queryset(user_filter.qs)
        forms = {
            "user_update_form": UserUpdateForm(self.request.user),
            "admin_create_form": AdminCreateForm(self.request.user),
            "manager_create_form": ManagerCreateForm(self.request.user),
            "set_password_form": SetPasswordForm(self.request.user),
            "filter": user_filter

        }
        context = {
            "paginator": paginator,
            "page_obj": page,
            "is_paginated": is_paginated,
            "users": page.object_list
        }
        context.update(forms)
        context.update(original_get_context_data_fn(self, *args, **kwargs))
        return context

    def paginate_queryset(queryset):
        paginator = Paginator(queryset, max_items_per_page)
        page = paginator.page(first_page)
        return paginator, page, page.object_list, page.has_other_pages()

    cls.get_context_data = get_context_data
    return cls
