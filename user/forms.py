from django.forms import ModelForm
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import PasswordResetForm  
from django import forms
from django.db.models import Q

from prepaid_meters_token_generator_system.utils.forms import BaseSearchForm

from user import account_types as user_account_types

ADMIN_ACCOUNT_CHOICES = (
    (user_account_types.MANAGER, "Manager"),
)
SUPER_ADMIN_ACCOUNT_CHOICES = (
    (user_account_types.ADMIN, "Admin"),
    (user_account_types.MANAGER, "Manager"),
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
        user_account_type = self.cleaned_data["account_type"]
        self.cleaned_data.pop("password_confirm", None)
        if user_account_type == user_account_types.ADMIN:
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


class EditUserProfileForm(EditUserForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        if self.user:
            user_fields = {
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "email": self.user.email,
                "address": self.user.address,
                "phone_no": self.user.phone_no,
            }
            initial = kwargs.get("initial", {})
            initial.update(user_fields)
            kwargs["initial"] = initial

        super(EditUserForm, self).__init__(*args, **kwargs)
        
        
class ResetPasswordForm(PasswordResetForm):
    email = None
    phone_no = forms.CharField(label="Phone Number", max_length=10)



class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(label="Current password", widget=forms.PasswordInput)
    new_password = forms.CharField(label="New password", widget=forms.PasswordInput)
    new_password_confirmation = forms.CharField(label="New password confirm", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)


    def clean_current_password(self):
        current_password = self.cleaned_data["current_password"]
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Invalid current password")
        
    def clean_new_password_confirmation(self):
        new_password = self.cleaned_data["new_password"]
        new_password_confirmation = self.cleaned_data["new_password_confirmation"]

        if new_password != new_password_confirmation:
            raise forms.ValidationError("Passwords must be the same")
       
        if password_validation.validate_password(new_password, self.user) is None:
            return new_password

    def update_password(self):
        self.user.set_password(self.cleaned_data["new_password"])
        self.user.save(update_fields=["password"])
        return self.user


class SearchForm(BaseSearchForm):
    model_search_field = "first_name"
