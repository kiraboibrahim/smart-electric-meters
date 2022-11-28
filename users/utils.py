from django.db.models import Q
from django.contrib.auth import get_user_model

from users.account_types import ADMIN, MANAGER
from users.forms import AdminCreateUserForm, SuperAdminCreateUserForm

User = get_user_model()


def get_users(authenticated_user, initial_users=None):
    users = initial_users.filter(Q(account_type=MANAGER)) if initial_users is not None else \
        User.objects.all().filter(Q(account_type=MANAGER))
    if authenticated_user.is_super_admin():
        users = users.filter(Q(account_type=ADMIN) | Q(account_type=MANAGER))
    return users


def get_add_user_form_class(authenticated_user):
    form_class = SuperAdminCreateUserForm if authenticated_user.is_super_admin() else AdminCreateUserForm
    return form_class
