from django.db import models
from django.contrib.auth import get_user_model

from meters.models import Meter

from .managers import PaymentManager
from .signals import payment_successful, payment_failed

User = get_user_model()


class Payment(models.Model):
    PAYMENT_PENDING = 1
    PAYMENT_FAILED = 2
    PAYMENT_SUCCESSFUL = 3

    STATUS_CHOICES = [
        (PAYMENT_PENDING, "PENDING"),
        (PAYMENT_FAILED, "FAILED"),
        (PAYMENT_SUCCESSFUL, "SUCCESSFUL")
    ]

    amount = models.PositiveIntegerField()
    status = models.PositiveIntegerField(choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    external_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    failure_reason = models.CharField(max_length=512, null=True, blank=True)

    objects = PaymentManager()

    class Meta:
        ordering = ["-created_at"]

    def is_failed(self):
        return self.status is self.PAYMENT_FAILED

    def is_pending(self):
        return self.status is self.PAYMENT_PENDING

    def is_successful(self):
        return self.status is self.PAYMENT_SUCCESSFUL

    def mark_as_failed(self, reason="Unknown"):
        if self.is_pending():
            return
        self.status = self.PAYMENT_FAILED
        self.failure_reason = reason
        self.save(update_fields=["status", "failure_reason"])
        payment_failed.send(sender=self.__class__, payment=self, associated_order=self.order)

    def mark_as_successful(self):
        if not self.is_pending():
            return
        self.status = self.PAYMENT_SUCCESSFUL
        self.save(update_fields=["status"])
        payment_successful.send(sender=self.__class__, payment=self, associated_order=self.order)

    def set_external_id(self, external_id):
        if self.external_id is not None:
            return
        self.external_id = external_id
        """
        Only update the external_id because without explicitly setting the fields to be updated, it may overwrite other 
        fields. This happens in cases where the payment backend is prepaid(instantly marks payment as successful) which 
        re-fetches the payment from db, and this makes it two places(pay() method of order & in this model) from where 
        the payment can be altered hence creating race conditions whose result is dependent upon the last modification 
        made. For the other payment backends, they are free from this problem because of their async nature
        """
        self.save(update_fields=["external_id"])

    def __str__(self):
        return f"{self.amount}"
