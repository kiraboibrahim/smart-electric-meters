import logging
import requests

from django.conf import settings as django_settings
from ..base import PaymentBackend, PaymentRequest
from ..excpetions import FailedPaymentException

from . import settings
from .payloads import PaymentRequestPayload

logger = logging.getLogger(__name__)


class PayLeoPaymentBackend(PaymentBackend):
    BASE_URL = "https://vendors.pay-leo.com/api/v2/test" if django_settings.DEBUG else "https://vendors.pay-leo.com" \
                                                                                                "/api/v2/live"
    MERCHANT_CODE = settings.PAYLEO_MERCHANT_CODE
    CONSUMER_KEY = settings.PAYLEO_CONSUMER_KEY
    CONSUMER_SECRET = settings.PAYLEO_CONSUMER_SECRET

    SUCCESSFUL_RESPONSE_CODE = 100
    FAILED_RESPONSE_CODE = 204

    def request_payment(self, payment_request: PaymentRequest):
        url = f"{self.BASE_URL}/deposit/"
        payload = PaymentRequestPayload(payment_request, url, self.MERCHANT_CODE, self.CONSUMER_KEY, self.CONSUMER_SECRET)
        try:
            proxies = django_settings.PROXIES if django_settings.DEBUG is True else {}
            response = requests.post(url, json=payload, proxies=proxies).json()
            if response["code"] == self.FAILED_RESPONSE_CODE:
                logger.error(f"{response['message']}")
                raise FailedPaymentException(f"{response['message']}")
            # Return the APIs transaction ID; This is different from the transactionId in the payload
            return response["transactionId"]
        except Exception as exc:
            logger.exception(str(exc))
            raise FailedPaymentException(str(exc))
