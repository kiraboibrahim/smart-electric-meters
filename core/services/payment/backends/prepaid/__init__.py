import random
import logging

from ..base import PaymentBackend, PaymentRequest
from ..excpetions import FailedPaymentException

from payments.models import Payment

logger = logging.getLogger(__name__)


class PrepaidPaymentBackend(PaymentBackend):
    """
    This payment backend immediately marks the payment as successful.
    """
    def request_payment(self, payment_request: PaymentRequest):
        try:
            payment = Payment.objects.get(pk=payment_request.payment_id)
        except Payment.DoesNotExist:
            logger.error(f"Payment failed: ID ({payment_request.payment_id}) doesn't exist in database")
            raise FailedPaymentException("Payment not found")
        payment.mark_as_successful()
        return self.get_transaction_id(payment_request.payment_id)

    @staticmethod
    def get_transaction_id(payment_id):
        random_num = "".join([str(random.randint(0, 9)) for _ in range(15)])
        transaction_id = f"{random_num}{payment_id}"
        return transaction_id
