from django.db import models

from meters.models import Meter

from payments.models import Payment


class RechargeToken(models.Model):
    token_no = models.CharField(max_length=255, unique=True)
    num_of_units = models.CharField(max_length=255)
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE, related_name="tokens")
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="tokens", null=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token_no
