from functools import cached_property

from django.core.validators import MaxValueValidator
from django.db import models

from .validators import is_not_default_meter_category


class MeterCategory(models.Model):
    percentage_charge = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    fixed_charge = models.PositiveIntegerField()
    label = models.CharField(max_length=255, unique=True, help_text="Keep it precise",
                             validators=[is_not_default_meter_category])

    @property
    def charges(self):
        return self.percentage_charge / 100, self.fixed_charge

    @cached_property
    def has_meters(self):
        return self.meters.exists()

    def __str__(self):
        return self.label

    class Meta:
        verbose_name_plural = "Meter categories"
