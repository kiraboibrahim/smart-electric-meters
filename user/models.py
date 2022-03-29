from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import PrepaidMeterUserManager
from .acc_types import NONE, SUPER_ADMIN, ADMIN, MANAGER
# Create your models here.

# Super Admin account mask    = 00000001
# Admin account mask          = 00000010
# Manager Account mask        = 00000100
acc_choices = [
    (NONE, "None"),
    (SUPER_ADMIN, "Super Admin"),
    (ADMIN, "Admin"),
    (MANAGER, "Manager"),
]

class PrepaidMeterUser(AbstractUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    # The target clients of the system are not so much of 'email people' 
    email = models.EmailField(unique=True, null=True, blank=True)
    # Phone number is only 10 digits long
    phone_no = models.CharField(max_length=10, unique=True)
    address = models.CharField(max_length=255)
    acc_type = models.PositiveIntegerField(choices=acc_choices)

    USERNAME_FIELD = "phone_no"
    REQUIRED_FIELDS = ["first_name", "last_name", 'address'] 
    objects = PrepaidMeterUserManager()


# The price_per_unit for each manager acccount
class PricePerUnit(models.Model):
    # Delete the priceperunit associated with the manager once the manager is deleted
    manager = models.OneToOneField(PrepaidMeterUser, unique=True, on_delete=models.CASCADE)
    price_per_unit = models.PositiveIntegerField()
