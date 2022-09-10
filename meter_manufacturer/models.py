from django.db import models


class MeterManufacturer(models.Model):
    name = models.CharField(max_length=255)
    telephone_contact = models.CharField(max_length=10)
    address = models.CharField(max_length=30)

    def __str__(self):
        return self.name
