from django import forms
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.contrib.auth import forms as auth_forms
from django.forms import ModelForm

from phonenumber_field.widgets import PhoneNumberPrefixWidget

import core.widgets as custom_widgets
from core import COUNTRY_CHOICES

from .account_types import ADMIN, MANAGER
from .models import UnitPrice
from .filters import UserFilter

User = get_user_model()


class BaseUserCreateForm(ModelForm):

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_no", "address"]
        labels = {
            "phone_no": "Phone number"
        }
        widgets = {
            "phone_no": PhoneNumberPrefixWidget(country_choices=COUNTRY_CHOICES)
        }
        help_texts = {
            "email": "You will need an email to reset your password"
        }


class AdminCreateForm(BaseUserCreateForm):
    ACCOUNT_TYPE = ADMIN

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        if not self.user.is_super_admin():
            raise PermissionDenied
        return User.objects.create_admin(**self.cleaned_data)


class ManagerCreateForm(BaseUserCreateForm):
    ACCOUNT_TYPE = MANAGER
    unit_price = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        initial = kwargs.get("initial", {})
        initial["unit_price"] = settings.LEGIT_SYSTEMS_DEFAULT_UNIT_PRICE
        kwargs.update({"initial": initial})
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        return User.objects.create_manager(**self.cleaned_data)


class UserUpdateForm(ModelForm):
    ACCOUNT_TYPE_CHOICES = (
        (MANAGER, "Manager"),
        (ADMIN, "Admin")
    )
    account_type = forms.ChoiceField(label="Account type", choices=ACCOUNT_TYPE_CHOICES)

    class Meta:
        model = User
        labels = {
            "phone_no": "Phone number"
        }
        fields = ["first_name", "last_name", "email", "phone_no", "address", "account_type"]
        widgets = {
            "phone_no": PhoneNumberPrefixWidget(country_choices=COUNTRY_CHOICES)
        }

    def __init__(self, updater, *args, **kwargs):
        self.updater = updater  # Who is updating the user?
        super().__init__(*args, **kwargs)
        if self.updater.is_admin():
            del self.fields["account_type"]  # Admins can't change to any account type

    def save(self, commit=True):
        to_be_updated_user = self.instance
        if to_be_updated_user.assert_same_account_type(self.updater) or to_be_updated_user.is_super_admin() or \
                to_be_updated_user.is_default_manager():
            raise PermissionDenied
        return super().save(commit)


class MyProfileUpdateForm(ModelForm):

    class Meta:
        model = User
        labels = {
            "phone_no": "Phone number"
        }
        fields = ["first_name", "last_name", "email", "phone_no", "address"]
        widgets = {
            "phone_no": PhoneNumberPrefixWidget(country_choices=COUNTRY_CHOICES)
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        initial = kwargs.get("initial", {})
        user_data = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "address": self.user.address,
            "phone_no": self.user.phone_no,
        }
        initial.update(user_data)
        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)
        if not self.user.email:
            self.fields["email"].help_text = "You won't be able to reset your password without an email"


class PasswordResetForm(auth_forms.PasswordResetForm):

    # Make request a required argument because it is required to get the full context
    def save(self, *args, **kwargs):
        request = kwargs["request"]
        kwargs["subject_template_name"] = "users/password_reset_email_subject.txt"
        kwargs["email_template_name"] = "users/password_reset_email.html"
        kwargs["html_email_template_name"] = kwargs["email_template_name"]
        kwargs["use_https"] = True
        kwargs["extra_email_context"] = {
            "browser_name": f"{request.user_agent.browser.family} {request.user_agent.browser.version_string}",
            "operating_system": f"{request.user_agent.os.family} {request.user_agent.os.version_string}",
        }
        kwargs["request"] = request
        kwargs["from_email"] = settings.FROM_EMAIL
        return super().save(**kwargs)


class PasswordChangeForm(auth_forms.PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget = custom_widgets.PasswordInput(attrs={"autocomplete": "current-password"})
        self.fields["old_password"].label = "Current password"
        self.fields["new_password1"].widget = custom_widgets.PasswordInput(attrs={"autocomplete": "new-password"})
        self.fields["new_password2"].widget = custom_widgets.PasswordInput(attrs={"autocomplete": "new-password"})


class SetPasswordForm(auth_forms.SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget = custom_widgets.PasswordInput(attrs={"auto-complete": "new-password"})


class AuthenticationForm(auth_forms.AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget = PhoneNumberPrefixWidget(attrs={"autofocus": True},
                                                                 country_choices=COUNTRY_CHOICES)
        self.fields["password"].widget = custom_widgets.PasswordInput(attrs={"autocomplete": "current-password"})


class UnitPriceUpdateForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        self.user = user
        initial = kwargs.get("initial", {})
        if self.user.is_manager():
            initial.update({"price": self.user.unit_price})
        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)

    class Meta:
        model = UnitPrice
        fields = ('price',)
        help_texts = {
            "price": "This is the price of one unit i.e. 1KWH. It applies to all your meters"
        }
