from django.forms import ModelForm
from .models import PrepaidMeterUser
from django import forms
from .acc_types import ADMIN, MANAGER

admin_acc_choices = (
    (MANAGER, "Manager"),
)

# Admins are not allowed to create SuperAdmin accounts, So this form is used for admin accounts
class AdminCreateUserForm(ModelForm):
    acc_type = forms.PositiveIntegerField(max_legnth=1, choices=admin_acc_choices)
    class Meta:
        model = PrepaidMeterUser
        fields = ["first_name", "last_name", "email", "phone_no", "address"]


super_admin_choices = (
    (ADMIN, "Admin"),
    (MANAGER, "Manager"),
)

# The super admin can create admins and managers, Use super admin account choices
class SuperAdminCreateUserForm(ModelForm):
    acc_type = forms.PositiveIntegerField(max_legnth=1, choices=super_admin_acc_choices)
    class Meta:
        model = PrepaidMeterUser
        fields = ["first_name", "last_name", "email", "phone_no", "address"]


class EditUserForm(ModelForm):
    class Meta:
        model = PrepaidMeterUser
        # The only fields that are allowed to be edited
        fields = ["first_name", "last_name", "email", "phone_no", "address"]
