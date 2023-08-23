from django.db import models


class PaymentManager(models.Manager):

    def create_pending_payment(self, amount, payer_phone_no):
        pending_payment = self.create(amount=amount, payer_phone_no=payer_phone_no, status=self.model.PAYMENT_PENDING)
        return pending_payment
