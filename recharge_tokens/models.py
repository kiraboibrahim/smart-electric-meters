from django.db import models

from meters.models import Meter

from payments.models import Payment


class RechargeToken(models.Model):
    token_no = models.CharField(max_length=255, unique=True)
    num_of_units = models.CharField(max_length=255)
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE, related_name="tokens")
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="tokens", null=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_recent_recharge_tokens_for_meter(cls, meter):
        return cls.objects.filter(meter=meter)[0:20]

    @property
    def meter_no(self):
        return self.meter.meter_no

    @property
    def payer_full_name(self):
        return self.payment.payer_full_name if self.payment else None

    @property
    def payer_phone_no(self):
        return self.payment.payer_phone_no if self.payment else None

    @property
    def amount_paid(self):
        return self.payment.amount_paid if self.payment else None

    def __str__(self):
        return self.token_no

    class Meta:
        ordering = ["-generated_at"]
