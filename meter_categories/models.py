from django.db import models
from django.core.validators import MaxValueValidator

class MeterCategory(models.Model):
    percentage_charge = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    fixed_charge = models.PositiveIntegerField()
    label = models.CharField(max_length=255, unique=True, help_text="Keep it precise ie: HomeCharges")

    @property
    def charges(self):
        return (self.percentage_charge/100, self.fixed_charge)
    
    def __str__(self):
        return self.label

    class Meta:
        verbose_name_plural = "Meter categories"
