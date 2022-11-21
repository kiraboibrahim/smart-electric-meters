import math

from django.db import models
from django.contrib.auth import get_user_model
 
import users.account_types as user_account_types

from manufacturers.models import MeterManufacturer

from meter_categories.models import MeterCategory

import external_api.models


User = get_user_model()

    
class Meter(models.Model):
    meter_no = models.CharField("Meter number", max_length=11, unique=True)
    manufacturer = models.ForeignKey(MeterManufacturer, on_delete=models.PROTECT, related_name="meters")
    manager = models.ForeignKey(User, on_delete=models.PROTECT,
                                limit_choices_to={"account_type": user_account_types.MANAGER}, null=True, blank=True,
                                related_name="meters")
    category = models.ForeignKey(MeterCategory, on_delete=models.PROTECT, null=True, blank=True, related_name="meters")
    is_active = models.BooleanField(default=True)

    def recharge(self, gross_recharge_amount, price_per_unit):
        net_recharge_amount = self.__get_net_recharge_amount(gross_recharge_amount)
        num_of_units = net_recharge_amount / price_per_unit
        recharge_token = external_api.models.Meter(self).recharge(num_of_units)
        recharge_token.meter = self
        return recharge_token

    def __get_net_recharge_amount(self, gross_recharge_amount):
        charges = (self.get_charges())(gross_recharge_amount)
        net_recharge_amount = gross_recharge_amount - charges
        return net_recharge_amount

    def register(self):
        return external_api.models.Meter(self).register()

    def get_charges(self):
        percentage_charge, fixed_charge = self.category.charges

        def calculate_charges(amount_paid):
            return fixed_charge + percentage_charge*amount_paid

        return calculate_charges

    def deactivate(self):
        self.is_active = False
        self.save()

    def activate(self):
        self.is_active = True
        self.save()

    @property
    def manufacturer_name(self):
        return self.manufacturer.name

    @property
    def manager_full_name(self):
        if self.manager:
            return self.manager.full_name

    @property
    def category_label(self):
        if self.category:
            return self.category.label

    @property
    def unit_price(self):
        return self.manager.price_per_unit

    def __str__(self):
        return "%s %s" % (self.meter_no, self.manager_full_name)

    class Meta:
        ordering = ["manager"]
