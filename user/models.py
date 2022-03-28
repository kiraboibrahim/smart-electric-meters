from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import PrepaidMeterUserManager
# Create your models here.

# Admin account mask    = 00000010
# Manager account mask  = 00000100
acc_choices = [
    (2, "Super Admin Account"),
    (4, "Admin Account"),
    (8, "Manager Account")
]

class PrepaidMeterUser(AbstractUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    # The target clients of the system are not so much of 'email people' 
    email = models.EmailField(unique=True, null=True)
    phone_no = models.PositiveIntegerField(unique=True, min_length=10, max_length=10)
    address = models.CharField(max_length=255)
    acc_type = models.PositiveIntegerField(max_length=1, choices=acc_choices)

    USERNAME_FIELD "phone_no"
    REQUIRED_FIELDS = ["first_name", "last_name", 'address'] 
    objects = PrepaidMeterUserManager()


# The price_per_unit for each manager acccount
class PricePerUnit(models.Model):
    # Delete the priceperunit associated with the manager once the manager is deleted
    manager = models.OnetoOneField(PrepaidMeterUser, unique=True, on_delete=models.CASCADE)
    price_per_unit = models.PositiveIntegerField()
