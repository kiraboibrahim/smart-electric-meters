from django.forms import ModelForm
from django.contrib.auth import get_user_model
from django import forms
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



class EditUserForm(ModelForm):
    class Meta:
        model = User
        # The only fields that are allowed to be edited
        fields = ["first_name", "last_name", "email", "phone_no", "address"]
