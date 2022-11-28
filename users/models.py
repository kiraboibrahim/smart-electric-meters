from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

from .managers import UserManager
from .account_types import DJANGO_SUPERUSER, SUPER_ADMIN, ADMIN, MANAGER
from .validators import is_not_default_manager


class User(AbstractUser):
    account_choices = [
        (DJANGO_SUPERUSER, "None"),
        (SUPER_ADMIN, "Super Admin"),
        (ADMIN, "Admin"),
        (MANAGER, "Manager"),
    ]

    username = None
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True,
                              help_text="Email will be used for resetting your password")
    phone_no = models.CharField(verbose_name="Phone number", max_length=10, unique=True,
                                validators=[is_not_default_manager])
    address = models.CharField(max_length=255)
    account_type = models.PositiveIntegerField(choices=account_choices)

    USERNAME_FIELD = "phone_no"
    REQUIRED_FIELDS = ["first_name", "last_name", 'address'] 

    objects = UserManager()

    def is_super_admin(self):
        return self.account_type == SUPER_ADMIN

    def is_admin(self):
        return self.account_type == ADMIN

    def is_manager(self):
        return self.account_type == MANAGER

    def is_default_manager(self):
        return self.phone_no == settings.DEFAULT_MANAGER_PHONE_NO

    @property
    def price_per_unit(self):
        if self.is_manager() and hasattr(self, "unit_price"):
            return self.unit_price.price

    @property
    def full_name(self):
        return "%s %s" % (self.first_name.title(), self.last_name.title())

    @property
    def num_of_associated_meters(self):
        if self.is_manager():
            return self.meters.count()
        return 0

    def assert_same_account_type(self, other_user):
        try:
            assert self.account_type == other_user.account_type
        except AssertionError:
            return False
        return True

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ['-date_joined']


class DefaultMeterManager(models.Model):
    manager = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={"account_type": MANAGER})

    def __str__(self):
        return self.manager.full_name


class UnitPrice(models.Model):
    manager = models.OneToOneField(User, related_name="unit_price", unique=True, on_delete=models.CASCADE,
                                   limit_choices_to={"account_type": MANAGER})
    label = models.CharField(default="API-STANDARD", max_length=255)
    price = models.PositiveIntegerField(default=1000)
