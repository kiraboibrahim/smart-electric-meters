from django.db import models
from django.contrib.auth.models import AbstractUser

from user.managers import PrepaidMeterUserManager
import user.account_types as user_account_types


account_choices = [
    (user_account_types.NONE, "None"),
    (user_account_types.SUPER_ADMIN, "Super Admin"),
    (user_account_types.ADMIN, "Admin"),
    (user_account_types.MANAGER, "Manager"),
]


class User(AbstractUser):
    username = None # Remove the username field
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    # The target clients of the system are not so much of 'email people' 
    email = models.EmailField(unique=True, null=True, blank=True)
    # Phone number is only 10 digits long
    phone_no = models.CharField(verbose_name="Phone number", max_length=10, unique=True)
    address = models.CharField(max_length=255)
    account_type = models.PositiveIntegerField(choices=account_choices)

    USERNAME_FIELD = "phone_no"
    REQUIRED_FIELDS = ["first_name", "last_name", 'address'] 
    objects = PrepaidMeterUserManager()

    @property
    def fullname(self):
        return "%s %s" %(self.first_name, self.last_name)
        
    def __str__(self):
        return self.fullname


    class Meta:
        ordering = ['-date_joined']


class UnitPrice(models.Model):
    manager = models.OneToOneField(User, related_name="unit_price", unique=True, on_delete=models.CASCADE, limit_choices_to={"account_type": user_account_types.MANAGER})
    label = models.CharField(default="API-STANDARD", max_length=255)
    price = models.PositiveIntegerField(default=1000)
