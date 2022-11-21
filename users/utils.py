from django.db.models import Q
from django.contrib.auth import get_user_model
from django.conf import settings

from users.account_types import ADMIN, SUPER_ADMIN, MANAGER
from users.forms import AdminCreateUserForm, SuperAdminCreateUserForm


MAX_ITEMS_PER_PAGE = settings.MAX_ITEMS_PER_PAGE
User = get_user_model()


def get_users(user):
    user_account_type = user.account_type
    users = User.objects.all().filter(Q(account_type=MANAGER))
    if user_account_type == SUPER_ADMIN:
        users = users.filter(Q(account_type=ADMIN) | Q(account_type=MANAGER))
    return users


def get_add_user_form_class(user):
    form_class = SuperAdminCreateUserForm if user.account_type == SUPER_ADMIN else AdminCreateUserForm
    return form_class
