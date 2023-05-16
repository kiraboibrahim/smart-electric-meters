from functools import cached_property

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import PasswordResetForm
from django.db.models import ObjectDoesNotExist
from django.forms import ModelForm

from shared.widgets import PasswordInput
from .account_types import ADMIN, MANAGER
from .models import UnitPrice

User = get_user_model()


class CreateUserBaseForm(ModelForm):
    password = forms.CharField(widget=PasswordInput)
    password_confirmation = forms.CharField(label="Confirm password", widget=PasswordInput)
    field_order = ["first_name", "last_name", "email", "phone_no", "address", "account_type"]

    def clean_password_confirmation(self):
        password = self.cleaned_data["password"]
        password_confirmation = self.cleaned_data["password_confirmation"]
        if password != password_confirmation:
            raise forms.ValidationError("Passwords must be the same")

    def save(self, commit=True):
        user_account_type = self.cleaned_data["account_type"]
        self.cleaned_data.pop("password_confirmation", None)
        if user_account_type == ADMIN:
            return User.objects.create_admin(**self.cleaned_data)
        else:
            return User.objects.create_manager(**self.cleaned_data)


class AdminCreateUserForm(CreateUserBaseForm):
    ADMIN_ACCOUNT_CHOICES = (
        (MANAGER, "Manager"),
    )
    account_type = forms.ChoiceField(label="Account type", choices=ADMIN_ACCOUNT_CHOICES)
    
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_no", "address"]
        labels = {
             "phone_no": "Phone number"
         }


class SuperAdminCreateUserForm(CreateUserBaseForm):
    SUPER_ADMIN_ACCOUNT_CHOICES = (
        (ADMIN, "Admin"),
        (MANAGER, "Manager"),
    )
    account_type = forms.ChoiceField(label="Account type", choices=SUPER_ADMIN_ACCOUNT_CHOICES)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_no", "address"]


class CreateUserFormFactory:
    @classmethod
    def get_form(cls, user):
        form = None
        if user.is_super_admin():
            form = SuperAdminCreateUserForm()
        elif user.is_admin():
            form = AdminCreateUserForm()
        return form


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
            initial_data = {
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "email": self.user.email,
                "address": self.user.address,
                "phone_no": self.user.phone_no,
            }
            initial = kwargs.get("initial", {})
            initial.update(initial_data)
            kwargs["initial"] = initial
        super(EditUserForm, self).__init__(*args, **kwargs)
        
        
class ResetPasswordForm(PasswordResetForm):
    email = None
    phone_no = forms.CharField(label="Phone number", max_length=10)

    @cached_property
    def user(self):
        user = None
        try:
            user = User.objects.get(phone_no=self.cleaned_data.get("phone_no"), is_active=True)
        except ObjectDoesNotExist:
            pass
        return user


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(label="Current password", widget=PasswordInput)
    new_password = forms.CharField(label="New password", widget=PasswordInput)
    new_password_confirmation = forms.CharField(label="New password confirm", widget=PasswordInput)

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

    def change_password(self):
        self.user.set_password(self.cleaned_data["new_password"])
        self.user.save(update_fields=["password"])
        return self.user


class ManagerUnitPriceEditForm(forms.ModelForm):

    class Meta:
        model = UnitPrice
        fields = ['price']
        help_texts = {
            "price": "This is the price of one unit ie 1KWH. It applies to all meters you own"
        }
