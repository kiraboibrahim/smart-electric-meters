from django.dispatch import receiver

from payments.models import Payment
from payments.signals import payment_successful


@receiver(payment_successful, sender=Payment)
def update_meter_last_payment_date(sender, payment, **kwargs):
    payment.order.meter.update_last_payment_date(payment.created_at)
