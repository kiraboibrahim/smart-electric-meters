from django.db.models import Q
from django import forms
from django.contrib.auth import get_user_model

import django_filters

from users.account_types import MANAGER, ADMIN

from . import account_types


MANAGERS = Q(account_type=account_types.MANAGER) | Q(account_type=account_types.DEFAULT_MANAGER)
MANAGERS_OR_ADMINS = MANAGERS | Q(account_type=account_types.ADMIN)


class UserFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method="filter_by_name")

    class Meta:
        model = get_user_model()
        fields = ("account_type", )

    def filter_by_name(self, queryset, field_name, value):
        # Look up names based on the first name or the last name
        return queryset.filter(Q(first_name__icontains=value) | Q(last_name__icontains=value))

    def get_form_class(self):
        base_form_class = super().get_form_class()
        admin_choices = (
            (MANAGER, "Manager"),
        )
        super_admin_choices = (
            (ADMIN, "Admin"),
            (MANAGER, "Manager"),
        )

        class FormClass(base_form_class):
            if self.request.user.is_admin():
                account_type = forms.ChoiceField(choices=admin_choices, required=False)
            elif self.request.user.is_super_admin():
                account_type = forms.ChoiceField(choices=super_admin_choices, required=False)
            else:
                account_type = None
        return FormClass

    @property
    def qs(self):
        users = super().qs
        return users.for_user(self.request.user)

