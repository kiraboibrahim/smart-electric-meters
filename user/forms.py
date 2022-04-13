from django.forms import ModelForm
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import PasswordResetForm  
from django import forms
from django.db.models import Q
from passwords.fields import PasswordField
from .acc_types import ADMIN, MANAGER

admin_acc_choices = (
    (MANAGER, "Manager"),
)

User = get_user_model()


class CreateUserBaseForm(ModelForm):
    password = PasswordField()
    password2 = PasswordField(label="Confirm Password")
    field_order = ["first_name", "last_name", "email", "phone_no", "address", "acc_type"]

    def clean_password2(self):
        password = self.cleaned_data["password"]
        password2 = self.cleaned_data["password2"]
        if password != password2:
            raise forms.ValidationError("Passwords must be the same")

        return password

    def save(self):
        first_name = self.cleaned_data["first_name"]
        last_name = self.cleaned_data["last_name"]
        phone_no = self.cleaned_data["phone_no"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]
        address = self.cleaned_data["address"]
        acc_type = int(self.cleaned_data["acc_type"]) # Convert to Integer

        user = None
        if acc_type == ADMIN:
            user = User.objects.create_admin(phone_no, first_name, last_name, address, password=password, email=email)
        elif acc_type == MANAGER:
            user = User.objects.create_manager(phone_no, first_name, last_name, address, password=password, email=email)

        return user


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    

# Admins are not allowed to create SuperAdmin accounts, So this form is used for admin accounts


class AdminCreateUserForm(CreateUserBaseForm):
    
    acc_type = forms.ChoiceField(label="Account Type", choices=admin_acc_choices)
    
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_no", "address"]


super_admin_acc_choices = (
    (ADMIN, "Admin"),
    (MANAGER, "Manager"),
)

# The super admin can create admins and managers, Use super admin account choices
class SuperAdminCreateUserForm(CreateUserBaseForm):
    acc_type = forms.ChoiceField(label="Account Type", choices=super_admin_acc_choices)
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_no", "address"]



class EditUserForm(forms.Form):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField(required=False)
    phone_no = forms.CharField(max_length=10)
    address = forms.CharField(max_length=255)

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        
    def clean_email(self):
        return self._clean("email")


    def clean_phone_no(self):
        return self._clean("phone_no")
        
    def _clean(self, field_name):
        new_field_value = self.cleaned_data[field_name]
        original_field_value = getattr(self.user, field_name, None)
        if new_field_value and new_field_value != original_field_value:
            # Field has been changed
            try:
                User.objects.get(Q(**{field_name:new_field_value}) & ~Q(id=self.user.id))
            except User.DoesNotExist:
                return new_field_value
            raise forms.ValidationError("Duplicate values are not allowed")
        
        return original_field_value
        
    def update(self):
        update_fields = []
        if self.user.first_name != self.cleaned_data["first_name"]:
            self.user.first_name = self.cleaned_data["first_name"]

        if self.user.last_name != self.cleaned_data["last_name"]:
            self.user.last_name = self.cleaned_data["last_name"]

        if self.user.phone_no != self.cleaned_data["phone_no"]:
            self.user.phone_no = self.cleaned_data["phone_no"]

        if self.user.address != self.cleaned_data["address"]:
            self.user.address = self.cleaned_data["address"]

        if self.user.email != self.cleaned_data["email"]:
            self.user.email = self.cleaned_data["email"]

        self.user.save()
        return self.user

class RevokePasswordForm(forms.Form):
    new_password = PasswordField(label="New password")

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        
    def clean_new_password(self):
        password = self.cleaned_data["new_password"]
        if password_validation.validate_password(password, self.user) is None:
            return password

    def revoke_password(self):
        self.user.set_password(self.cleaned_data["password"])
        self.user.save(update_fields=["password"])
        return self.user
        
        
class ResetPasswordForm(PasswordResetForm):
    email = None
    phone_no = forms.CharField(label="Phone Number", max_length=10)
