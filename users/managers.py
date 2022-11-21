from django.contrib.auth.base_user import BaseUserManager

from users.account_types import DJANGO_SUPERUSER, SUPER_ADMIN, ADMIN, MANAGER


class UserManager(BaseUserManager):
    def create_user(self, phone_no, first_name, last_name, address, password=None,  **extra_fields):
        extra_fields.setdefault("email")
        if extra_fields["email"]:
            extra_fields["email"] = self.normalize_email(extra_fields["email"])
            
        user = self.model(first_name=first_name, last_name=last_name, phone_no=phone_no, address=address, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_manager(self, phone_no, first_name, last_name, address, password=None, **extra_fields):
        extra_fields["account_type"] = MANAGER
        user = self.create_user(phone_no, first_name, last_name, address, password, **extra_fields) 
        return user

    def create_admin(self, phone_no, first_name, last_name, address, password=None, **extra_fields):
        extra_fields["account_type"] =  ADMIN
        user = self.create_user(phone_no, first_name, last_name, address, password, **extra_fields) 
        return user

    def create_super_admin(self, phone_no, first_name, last_name, address, password=None, **extra_fields):
        extra_fields["account_type"] = SUPER_ADMIN
        user = self.create_user(phone_no, first_name, last_name, address, password, **extra_fields) 
        return user

    def create_superuser(self, phone_no, first_name, last_name, address, password=None, **extra_fields):
        extra_fields["account_type"] = DJANGO_SUPERUSER
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        user = self.create_user(phone_no, first_name, last_name, address, password, **extra_fields) 
        return user



    
