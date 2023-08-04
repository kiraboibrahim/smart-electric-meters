from django.db import models
from django.contrib.auth import get_user_model

from meters.models import Meter

from .managers import PaymentManager
from .signals import payment_successful, payment_failed
from .payment_status import PAYMENT_FAILED, PAYMENT_SUCCESSFUL, PAYMENT_PENDING

User = get_user_model()


class Payment(models.Model):
    STATUS_CHOICES = (
        (PAYMENT_PENDING, "PENDING"),
        (PAYMENT_FAILED, "FAILED"),
        (PAYMENT_SUCCESSFUL, "SUCCESSFUL")
    )
    amount = models.PositiveIntegerField()
    status = models.PositiveIntegerField(choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    external_id = models.CharField(max_length=255, unique=True, null=True)
    failure_reason = models.CharField(max_length=512, null=True)

    objects = PaymentManager()

    class Meta:
        ordering = ["-created_at"]

    def is_failed(self):
        return self.status == PAYMENT_FAILED

    def is_pending(self):
        return self.status == PAYMENT_PENDING

    def is_successful(self):
        return self.status == PAYMENT_SUCCESSFUL

    def mark_as_failed(self, reason="Unknown"):
        self.status = PAYMENT_FAILED
        self.failure_reason = reason
        self.save()
        payment_failed.send(sender=self.__class__, payment=self)

    def mark_as_successful(self):
        self.status = PAYMENT_SUCCESSFUL
        self.save()
        payment_successful.send(sender=self.__class__, payment=self)

    def deliver_order(self):
        return self.order.deliver()

    def retry(self):
        if self.is_failed():
            pass

    def __str__(self):
        return self.amount
