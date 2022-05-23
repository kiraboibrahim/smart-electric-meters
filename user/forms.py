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
        acc_type = self.cleaned_data["acc_type"]
        del self.cleaned_data["password2"] # Not required for user creation
        if acc_type == ADMIN:
            return User.objects.create_admin(**self.cleaned_data)
        else:
            return User.objects.create_manager(**self.cleaned_data)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    

# Admins are not allowed to create SuperAdmin accounts, So this form is used for admin accounts


class AdminCreateUserForm(CreateUserBaseForm):
    
    acc_type = forms.ChoiceField(label="Account type", choices=admin_acc_choices)
    
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_no", "address"]
        labels = {
             "phone_no": "Phone number"
         }


super_admin_acc_choices = (
    (ADMIN, "Admin"),
    (MANAGER, "Manager"),
)

# The super admin can create admins and managers, Use super admin account choices
class SuperAdminCreateUserForm(CreateUserBaseForm):
    acc_type = forms.ChoiceField(label="Account type", choices=super_admin_acc_choices)
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_no", "address"]



class EditUserForm(ModelForm):

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        
    class Meta:
        model = User
        labels = {
            "phone_no": "Phone number"
        }
        fields = ["first_name", "last_name", "email", "phone_no", "address"]


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
        self.user.set_password(self.cleaned_data["new_password"])
        self.user.save(update_fields=["password"])
        return self.user
        
        
class ResetPasswordForm(PasswordResetForm):
    email = None
    phone_no = forms.CharField(label="Phone Number", max_length=10)
