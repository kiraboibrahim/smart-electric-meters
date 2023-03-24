from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q

from .account_types import DJANGO_SUPERUSER, SUPER_ADMIN, ADMIN, MANAGER, DEFAULT_MANAGER
from .managers import UserManager
from .validators import is_not_default_manager


class User(AbstractUser):
    account_choices = [
        (DJANGO_SUPERUSER, "None"),
        (SUPER_ADMIN, "Super Admin"),
        (ADMIN, "Admin"),
        (MANAGER, "Manager"),
        (DEFAULT_MANAGER, "Default Manager")
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
        return self.phone_no == settings.DEFAULTS["MANAGER"]["phone_no"]

    @property
    def price_per_unit(self):
        """
        The name is 'price_per_unit'(it could have been 'unit_price') because the related manager goes by the name 'unit_price'
        """
        if (self.is_manager() or self.is_default_manager()) and hasattr(self, "unit_price"):
            return self.unit_price.price

    @property
    def full_name(self):
        return "%s %s" % (self.first_name.title(), self.last_name.title())

    def has_associated_meters(self):
        if self.num_of_associated_meters == 0:
            return False
        return True

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


class UnitPrice(models.Model):
    manager = models.OneToOneField(User, related_name="unit_price", unique=True, on_delete=models.CASCADE,
                                   limit_choices_to=Q(account_type=MANAGER) | Q(account_type=DEFAULT_MANAGER))
    label = models.CharField(default="API-STANDARD", max_length=255)
    price = models.PositiveIntegerField(default=1000)

    def __str__(self):
        return "{} - UGX {}".format(self.manager, self.price)

