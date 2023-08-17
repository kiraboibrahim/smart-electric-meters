import json
from django.db import models
from django.core.serializers import serialize

from phonenumber_field.modelfields import PhoneNumberField

from vendor_api.vendors import factory


class MeterVendor(models.Model):
    name = models.CharField(max_length=255)
    phone_no = PhoneNumberField(verbose_name="Phone number")
    address = models.CharField(max_length=30)

    class Meta:
        ordering = ("name", )

    @property
    def meter_count(self):
        return self.meters.all().count()

    def has_meters(self):
        return self.meters.exists()

    def is_api_available(self):
        return factory.is_vendor_api_available(self.name)

    def as_json(self):
        data = json.loads(serialize("json", [self])[1:-1])["fields"]
        data["phone_no"] = self.phone_no.national_number
        return json.dumps(data)

    def __str__(self):
        return self.name
