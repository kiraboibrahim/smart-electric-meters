# A custom manager for creating users
from django.contrib.auth.base_user import BaseUserManager
from .acc_types import NONE, SUPER_ADMIN, ADMIN, MANAGER

class PrepaidMeterUserManager(BaseUserManager):
    def create_user(self, phone_no, first_name, last_name, address, password=None,  **extra_fields):
        # If no email has been, It will be None
        extra_fields.setdefault("email")
        if extra_fields["email"]:
            extra_fields["email"] = self.normalize_email(extra_fields["email"])
            
        user = self.model(first_name=first_name, last_name=last_name, phone_no=phone_no, address=address, **extra_fields)

        user.set_password(password)

        # Save the user
        user.save()
    
        return user

    
    def create_manager(self, phone_no, first_name, last_name, address, password=None, **extra_fields):
        extra_fields.setdefault("acc_type", MANAGER)
        user = self.create_user(phone_no, first_name, last_name, address, password, **extra_fields) 
        return user

    
    def create_admin(self, phone_no, first_name, last_name, address, password=None, **extra_fields):
        extra_fields.setdefault("acc_type", ADMIN)
        user = self.create_user(phone_no, first_name, last_name, address, password, **extra_fields) 
        return user

    def create_superadmin(self, phone_no, first_name, last_name, address, password=None, **extra_fields):
        # This method creates super admins
        extra_fields.setdefault("acc_type", SUPER_ADMIN)
        user = self.create_user(phone_no, first_name, last_name, address, password, **extra_fields) 
        return user

    def create_superuser(self, phone_no, first_name, last_name, address, password=None, **extra_fields):
        # since acc_type is a required field when creating a new user, I am using a NONE account type because superusers are not analogous to super admins
        extra_fields.setdefault("acc_type", NONE)
        # This is django's superuser account creation method
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        user = self.create_user(phone_no, first_name, last_name, address, password, **extra_fields) 
        return user



    
