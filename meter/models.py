from django.db import models
from django.contrib.auth import get_user_model
 
import user.account_types as user_account_types

from meter_manufacturer.models import MeterManufacturer
from meter_category.models import MeterCategory

User = get_user_model()

    
class Meter(models.Model):
    meter_no = models.CharField("Meter number", max_length=11, unique=True)
    manufacturer = models.ForeignKey(MeterManufacturer, on_delete=models.PROTECT, related_name="meters")
    manager = models.ForeignKey(User, on_delete=models.PROTECT, limit_choices_to={"account_type": user_account_types.MANAGER}, null=True, blank=True, related_name="meters")
    category = models.ForeignKey(MeterCategory, on_delete=models.PROTECT, null=True, blank=True, related_name="meters")
    is_active = models.BooleanField(default=True)

    def get_charges(self):
        percentage_charge, fixed_charge = self.category.get_charges()

        def calculate_charges(amount_paid):
            return fixed_charge + percentage_charge*amount_paid

        return calculate_charges
        
    def __str__(self):
        return "%s %s" %(self.meter_no, self.manager.get_fullname())

    class Meta:
        ordering = ["manager"]
