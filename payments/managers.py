from django.db import models

from .payment_status import PAYMENT_PENDING


class PaymentManager(models.Manager):

    def create_pending_payment(self, amount):
        pending_payment = self.create(amount=amount, status=PAYMENT_PENDING)
        return pending_payment
