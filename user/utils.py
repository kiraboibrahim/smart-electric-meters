from django.db.models import Q
from django.contrib.auth import get_user_model
from django.conf import settings

from prepaid_meters_token_generator_system.utils.paginator import paginate_queryset, get_page_number
from prepaid_meters_token_generator_system.forms import SearchForm

from user.account_types import ADMIN, SUPER_ADMIN, MANAGER
import user.forms as user_forms

MAX_ITEMS_PER_PAGE = settings.MAX_ITEMS_PER_PAGE
User = get_user_model()


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


def is_forbidden_user_model_operation(operation):
    operation_type = operation[0]
    operation_caller = operation[1]
    operation_callee = operation[2]
    
    return (operation_caller.account_type, operation_callee.account_type) in FORBIDDEN_ADMINS_OPS_ON_USER_MODEL[operation_type]


def apply_user_filters(logged_in_user, users):
    logged_in_user_account_type = logged_in_user.account_type
    if logged_in_user_account_type == SUPER_ADMIN:
        users.filter(
            Q(account_type=MANAGER) | Q(account_type=ADMIN))
    else:
        users.filter(Q(account_type=MANAGER))

    return users


def get_add_user_form_class(logged_in_user):
    form_class = None
    if logged_in_user.account_type == SUPER_ADMIN:
        form_class = user_forms.SuperAdminCreateUserForm
    else:
        form_class = user_forms.AdminCreateUserForm
    return form_class


def get_list_users_template_forms(request, context):
    logged_in_user = request.user
    add_user_form_class = get_add_user_form_class(logged_in_user)
    add_user_form = context.get("add_user_form", add_user_form_class())
    search_user_form = context.get("search_user_form", SearchForm(request.GET))
    return add_user_form, search_user_form


def get_list_users_template_context_data(request, base_context={}):
    logged_in_user = request.user

    add_user_form, search_user_form = get_list_users_template_forms(request, base_context)
    user_queryset = base_context.get("users", User.objects.all())
    paginator = paginate_queryset(user_queryset, MAX_ITEMS_PER_PAGE)
    
    page_number = get_page_number(request)
    page = paginator.page(page_number)

    base_context["add_user_form"] = add_user_form
    base_context["search_user_form"] = search_user_form
    base_context["users"] = page.object_list
    base_context["paginator"] = paginator
    base_context["page_obj"] = page
    return base_context
