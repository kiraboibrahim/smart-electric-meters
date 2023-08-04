import json

from django.db import models
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AbstractUser
from django.core.serializers import serialize

from phonenumber_field.modelfields import PhoneNumberField

from core.services.notification import send_notification
from core.services.notification.strategies import BY_SMS, BY_EMAIL
from .account_types import DJANGO_ADMIN, SUPER_ADMIN, ADMIN, MANAGER, DEFAULT_MANAGER
from .managers import UserManager
from .filters import MANAGERS, MANAGERS_OR_ADMINS


class UserQuerySet(models.QuerySet):
    def managers(self):
        return self.filter(MANAGERS)

    def for_user(self, user):
        if user.is_super_admin():
            return self.filter(MANAGERS_OR_ADMINS).exclude(account_type=DEFAULT_MANAGER)
        return self.managers()


class User(AbstractUser):
    account_choices = [
        (DJANGO_ADMIN, "Django Admin"),
        (SUPER_ADMIN, "Super Admin"),
        (ADMIN, "Admin"),
        (MANAGER, "Manager"),
        (DEFAULT_MANAGER, "Default Manager")
    ]
    SERIALIZABLE_FIELDS = ("first_name", "last_name", "email", "address", "phone_no", "account_type")

    username = None
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_no = PhoneNumberField(verbose_name="Phone number", unique=True)
    address = models.CharField(max_length=255)
    account_type = models.PositiveIntegerField(choices=account_choices, default=MANAGER)

    USERNAME_FIELD = "phone_no"
    REQUIRED_FIELDS = ["first_name", "last_name", 'address'] 

    objects = UserManager.from_queryset(UserQuerySet)()

    class Meta:
        ordering = ['-date_joined']

    @property
    def meter_count(self):
        return self.meters.count() if (self.is_manager() or self.is_default_manager()) else 0

    @property
    def full_name(self):
        first_name = self.first_name.lower().title()
        last_name = self.last_name.lower().title()
        return f"{first_name} {last_name}"

    @property
    def unit_price(self):
        return self.unitprice.price

    def is_super_admin(self):
        return self.account_type == SUPER_ADMIN

    def is_admin(self):
        return self.account_type == ADMIN

    def is_manager(self):
        return self.account_type == MANAGER

    def is_default_manager(self):
        return self.account_type == DEFAULT_MANAGER

    def has_meters(self):
        return self.meter_count != 0

    def assert_same_account_type(self, other_user):
        try:
            assert self.account_type == other_user.account_type
        except AssertionError:
            return False
        return True

    def delete(self, using=None, keep_parents=False):
        if self.is_default_manager():
            raise PermissionDenied
        return super().delete(using, keep_parents)

    def save(self, *args, **kwargs):
        if self.id and self.is_default_manager():  # Editing the default manager
            raise PermissionDenied
        return super().save(*args, **kwargs)

    def notify_by_email(self, subject, message):
        if self.email:
            send_notification([self.email], subject, message, notification_strategy=BY_EMAIL)

    def notify_by_sms(self, subject, message):
        send_notification([str(self.phone_no).lstrip("+")], subject, message, notification_strategy=BY_SMS)

    def as_json(self):
        attrs = json.loads(serialize("json", [self])[1:-1])["fields"]  # Include sensitive information
        new_attrs = {}
        # Remove sensitive information
        for attr in attrs:
            if attr in self.SERIALIZABLE_FIELDS:
                new_attrs[attr] = attrs[attr]
        new_attrs["phone_no"] = self.phone_no.national_number  # Strip off the country code
        return json.dumps(new_attrs)

    def __str__(self):
        return self.full_name


class UnitPrice(models.Model):
    price = models.PositiveIntegerField(default=1000)
    manager = models.OneToOneField(User, unique=True, on_delete=models.CASCADE, limit_choices_to=MANAGERS)

    def __truediv__(self, other):
        return other / self.price

    def __str__(self):
        return self.price
