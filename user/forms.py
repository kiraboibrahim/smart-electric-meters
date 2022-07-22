from django.forms import ModelForm
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import PasswordResetForm  
from django import forms
from django.db.models import Q
from user.account_types import ADMIN, MANAGER

ADMIN_ACCOUNT_CHOICES = (
    (MANAGER, "Manager"),
)
SUPER_ADMIN_ACCOUNT_CHOICES = (
    (ADMIN, "Admin"),
    (MANAGER, "Manager"),
)


User = get_user_model()


class CreateUserBaseForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(label="Confirm password", widget=forms.PasswordInput)
    field_order = ["first_name", "last_name", "email", "phone_no", "address", "account_type"]

    def clean_password_confirm(self):
        password = self.cleaned_data["password"]
        password_confirm = self.cleaned_data["password_confirm"]
        if password != password_confirm:
            raise forms.ValidationError("Passwords must be the same")

        return password

    def save(self):
        account_type = self.cleaned_data["account_type"]
        self.cleaned_data.pop("password_confirm", None)
        if account_type == ADMIN:
            return User.objects.create_admin(**self.cleaned_data)
        else:
            return User.objects.create_manager(**self.cleaned_data)

# A form used by admins to register users, their account choices are limited as compared to superadmins
class AdminCreateUserForm(CreateUserBaseForm):
    account_type = forms.ChoiceField(label="Account type", choices=ADMIN_ACCOUNT_CHOICES)
    
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_no", "address"]
        labels = {
             "phone_no": "Phone number"
         }

# The super admin can create admins and managers, Use super admin account choices
class SuperAdminCreateUserForm(CreateUserBaseForm):
    account_type = forms.ChoiceField(label="Account type", choices=SUPER_ADMIN_ACCOUNT_CHOICES)
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_no", "address"]



class EditUserForm(ModelForm):
        
    class Meta:
        model = User
        labels = {
            "phone_no": "Phone number"
        }
        fields = ["first_name", "last_name", "email", "phone_no", "address"]


class RevokePasswordForm(forms.Form):
    new_password = forms.CharField(label="New password", widget=forms.PasswordInput)

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        
    def clean_new_password(self):
        password = self.cleaned_data["new_password"]
        if password_validation.validate_password(password, self.user) is None:
            return password

    def revoke_password(self):
        self.user.set_password(self.cleaned_data["new_password"])
        self.user.save(update_fields=["password"])
        return self.user
        
        
class ResetPasswordForm(PasswordResetForm):
    email = None
    phone_no = forms.CharField(label="Phone Number", max_length=10)
