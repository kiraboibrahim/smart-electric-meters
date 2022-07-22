from django.db import models
from django.contrib.auth.models import AbstractUser
from user.managers import PrepaidMeterUserManager
from user.account_types import NONE, SUPER_ADMIN, ADMIN, MANAGER
# Create your models here.

# Super Admin account mask    = 00000001
# Admin account mask          = 00000010
# Manager Account mask        = 00000100
account_choices = [
    (NONE, "None"),
    (SUPER_ADMIN, "Super Admin"),
    (ADMIN, "Admin"),
    (MANAGER, "Manager"),
]

class PrepaidMeterUser(AbstractUser):
    username = None # Remove the username field
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    # The target clients of the system are not so much of 'email people' 
    email = models.EmailField(unique=True, null=True, blank=True)
    # Phone number is only 10 digits long
    phone_no = models.CharField(verbose_name="Phone Number", max_length=10, unique=True)
    address = models.CharField(max_length=255)
    account_type = models.PositiveIntegerField(choices=account_choices)

    USERNAME_FIELD = "phone_no"
    REQUIRED_FIELDS = ["first_name", "last_name", 'address'] 
    objects = PrepaidMeterUserManager()

    def __str__(self):
        return "%s %s" %(self.first_name, self.last_name)


# The Unit Price for the manager, It applies to all meters owned by the manager
class UnitPrice(models.Model):
    # CASCADE: Delete the unitprice associated with the manager once the manager is deleted
    manager = models.OneToOneField(PrepaidMeterUser, related_name="unit_price", unique=True, on_delete=models.CASCADE, limit_choices_to={"account_type": MANAGER})
    label = models.CharField(default="API-STANDARD", max_length=255, unique=True)
    price = models.PositiveIntegerField(default=1000)
