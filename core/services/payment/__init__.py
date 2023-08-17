from django.conf import settings
from django.utils.module_loading import import_string

from .backends.base import PaymentRequest


# This is the entry point that all apps will use to access payment services
def request_payment(payment_id, amount, payer_msisdn):
    payment_request = PaymentRequest(payment_id, amount, payer_msisdn)
    payment_backend = import_string(settings.LEGIT_SYSTEMS_PAYMENT_BACKEND)()
    return payment_backend.request_payment(payment_request)
