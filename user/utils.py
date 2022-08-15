from django.db.models import Q
from django.contrib.auth import get_user_model

import user.account_types as user_account_types
import user.forms as user_forms


class ModelOperations:
    EDIT = 1
    DELETE = 2

# Forbidden operations of Administrators and Super Administrators: Format = (caller, callee)
FORBIDDEN_ADMINS_OPS_ON_USER_MODEL = {
    ModelOperations.EDIT: [
        (user_account_types.ADMIN, user_account_types.SUPER_ADMIN),
        (user_account_types.ADMIN, user_account_types.ADMIN),
        (user_account_types.SUPER_ADMIN, user_account_types.SUPER_ADMIN),
    ]
}
FORBIDDEN_ADMINS_OPS_ON_USER_MODEL[ModelOperations.DELETE] = FORBIDDEN_ADMINS_OPS_ON_USER_MODEL[ModelOperations.EDIT]     

def is_forbidden_user_model_operation(operation):
    operation_type = operation[0]
    operation_caller = operation[1]
    operation_callee = operation[2]
    
    return (operation_caller.account_type, operation_callee.account_type) in FORBIDDEN_ADMINS_OPS_ON_USER_MODEL[operation_type]


def get_users(logged_in_user):
    User = get_user_model()
    users = None
    
    logged_in_user_account_type = logged_in_user.account_type
    if logged_in_user_account_type == user_account_types.SUPER_ADMIN:
        users = User.objects.filter(Q(account_type=user_account_types.MANAGER) | Q(account_type=user_account_types.ADMIN))
    else:
        users= User.objects.filter(Q(account_type=user_account_types.MANAGER))

    return users

def get_add_user_form_class(logged_in_user):
    form_class = None
    
    if logged_in_user.account_type == user_account_types.SUPER_ADMIN:
        form_class = user_forms.SuperAdminCreateUserForm
    else:
        form_class = user_forms.AdminCreateUserForm
        
    return form_class

def get_list_users_template_context_data(request, base_context={}):
    logged_in_user = request.user
        
    add_user_form_class = get_add_user_form_class(logged_in_user)
    add_user_form = add_user_form_class()
    search_form = user_forms.SearchForm()
    users = get_users(logged_in_user)
        
    base_context.setdefault("add_user_form", add_user_form)
    base_context.setdefault("search_form", search_form)
    base_context.setdefault("users", users)
        
    return base_context
        
