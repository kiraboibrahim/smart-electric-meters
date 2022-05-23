from django.db import models
from django.core.validators import MaxValueValidator
from django.contrib.auth import get_user_model
from django.urls import reverse

# Create your models here.


class MeterCategory(models.Model):
    percentage_charge = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    fixed_charge = models.PositiveIntegerField()
    label = models.CharField(max_length=255, unique=True, help_text="Keep it precise ie: HomeCharges")

    def __str__(self):
        return self.label


class Manufacturer(models.Model):
    # The name of the manufacturer is strongly coupled to api classes in the api.py, so developers and admins
    # collaborate
    name = models.CharField("Manufacturer's Name", max_length=255)

    def __str__(self):
        return self.name
    
class Meter(models.Model):
    # Meter numbers have a length of 11
    meter_no = models.CharField("Meter Number", max_length=11, unique=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    # If a manager is deleted, the meter owner will be set NULL ie disowning all from the manager
    manager = models.ForeignKey(get_user_model(), models.SET_NULL, null=True, blank=True)
    # Prevent deletion of meter types if there are still child rows referencing it
    meter_category = models.ForeignKey(MeterCategory, on_delete=models.PROTECT)
        
    def __str__(self):
        return self.meter_no
    



class TokenHistory(models.Model):
    # From the decision reached, the name field is not necessary, and thus it is allowed to have NULL values
    name = models.CharField("Purchaser's Name", max_length=255, null=True)
    # When a user who bought a token is deleted from the database, then all child rows in this table will be set to NULL
    user = models.ForeignKey(get_user_model(), models.SET_NULL, null=True)
    token_no = models.PositiveIntegerField(unique=True)
    phone_no = models.CharField(max_length=10)
    # Amount of money paid
    amount_paid = models.CharField(max_length=255)
    # How many token units purchased
    num_token_units = models.CharField(max_length=255)
    # Automatically populate with the current date and time 
    purchased_at = models.DateTimeField(auto_now_add=True)
    # Meter for which token was generated, I don't see any reason why one would delete a meter that is already
    # in production, but if that happens and there are still any child rows(token history)  still referencing
    # a meter, prevent deletion 
    meter = models.ForeignKey(Meter, on_delete=models.PROTECT)


    def __str__(self):
        return self.name
