from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Payment(models.Model):
    user = models.ForeignKey(User, models.SET_NULL, null=True)
    amount_paid = models.PositiveIntegerField()
    charges = models.PositiveIntegerField()
    paid_at = models.DateTimeField(auto_now_add=True)
    is_virtual = models.BooleanField(default=True)

    @property
    def payer_phone_no(self):
        return self.user.phone_no if self.user else None

    def payer_full_name(self):
        return self.user.full_name if self.user else None

    def __str__(self):
        return "%s paid %s" % self.id

    class Meta:
        ordering = ["-paid_at"]
