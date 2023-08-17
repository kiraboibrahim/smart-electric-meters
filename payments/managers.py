from django.db import models


class PaymentManager(models.Manager):

    def create_pending_payment(self, amount):
        pending_payment = self.create(amount=amount, status=self.model.PAYMENT_PENDING)
        return pending_payment
