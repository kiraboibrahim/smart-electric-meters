import logging

from ..base import PaymentBackend, PaymentRequest
from ..excpetions import FailedPaymentException

from payments.models import Payment

logger = logging.getLogger(__name__)


class PrepaidPaymentBackend(PaymentBackend):
    """
    This payment backend immediately marks the payment as successful
    """
    def request_payment(self, payment_request: PaymentRequest):
        try:
            payment = Payment.objects.get(pk=payment_request.payment_id)
        except Payment.DoesNotExist:
            logger.error("Payment doesn't exist in database")
            raise FailedPaymentException
        payment.mark_as_successful()

