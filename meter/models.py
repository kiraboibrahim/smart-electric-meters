from django.db import models
from django.core.validators import MaxValueValidator
from django.contrib.auth import get_user_model
from django.urls import reverse

from user.account_types import MANAGER

User = get_user_model()
# Create your models here.


class MeterCategory(models.Model):
    percentage_charge = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    fixed_charge = models.PositiveIntegerField()
    label = models.CharField(max_length=255, unique=True, help_text="Keep it precise ie: HomeCharges")

    def __str__(self):
        return self.label


class Manufacturer(models.Model):
    # The name of the manufacturer is strongly coupled to exernal API classes, so developers and admins
    # have to communicate
    name = models.CharField(max_length=255)
    telephone_contact = models.CharField(max_length=10)
    address = models.CharField(max_length=30)

    def __str__(self):
        return self.name
    
class Meter(models.Model):
    meter_no = models.CharField("Meter Number", max_length=11, unique=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    # If a manager is deleted, the meter owner will be set NULL ie disowning all from the manager
    manager = models.ForeignKey(User, on_delete=models.PROTECT, limit_choices_to={"account_type": MANAGER})
    # Prevent deletion of meter categories if there are still meter child rows referencing it
    category = models.ForeignKey(MeterCategory, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
        
    def __str__(self):
        return self.meter_no
    



class TokenLog(models.Model):
    user = models.ForeignKey(User, models.SET_NULL, null=True)
    meter = models.ForeignKey(Meter, on_delete=models.PROTECT)
    token_no = models.CharField(max_length=255, unique=True)
    amount_paid = models.CharField(max_length=255)
    num_of_units = models.CharField(max_length=255)
    generated_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.name
