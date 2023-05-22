from django.core.validators import MaxValueValidator
from django.db import models

from .managers import ChargesCategoryManager


class MeterCategory(models.Model):
    percentage_charge = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    fixed_charge = models.PositiveIntegerField()
    label = models.CharField(max_length=255, unique=True, help_text="A unique name to identify this charges category")
    is_default = models.BooleanField(default=False)
    objects = ChargesCategoryManager()

    @property
    def charges(self):
        return self.percentage_charge / 100, self.fixed_charge

    def has_meters(self):
        return self.meters.exists()

    def __str__(self):
        return self.label

    class Meta:
        verbose_name_plural = "Meter categories"

