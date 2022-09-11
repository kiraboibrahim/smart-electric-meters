from django.db import models
from django.contrib.auth import get_user_model

from meter.models import Meter


User = get_user_model()


class Payment(models.Model):
    user = models.ForeignKey(User, models.SET_NULL, null=True)
    amount_paid = models.CharField(max_length=255)
    charges = models.CharField(max_length=255)
    paid_at = models.DateTimeField(auto_now_add=True)
    meter_no = models.CharField(max_length=11)
    num_of_units = models.CharField(max_length=255)

    @property
    def payer_phone_no(self):
        return self.user.full_name
        
    def __str__(self):
        return "%s paid %s".format(self.user.fullname, self.amount_paid)

    class Meta:
        ordering = ["-paid_at"]

    
class TokenLog(models.Model):
    meter = models.ForeignKey(Meter, on_delete=models.PROTECT)
    token_no = models.CharField(max_length=255, unique=True)
    num_of_units = models.CharField(max_length=255)
    generated_at = models.DateTimeField(auto_now_add=True)
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT)
    

    def __str__(self):
        return "%s - %s" %(self.meter.meter_no, self.token_no)

    class Meta:
        ordering = ["-generated_at"]
