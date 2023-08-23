import hmac
import hashlib

from ..excpetions import FailedPaymentException
from .settings import PAYLEO_MIN_TRANSACTION_AMOUNT, PAYLEO_CLIENT_TRANSACTION_ID_LENGTH


class PaymentRequestPayload(dict):

    def __init__(self, payment_request, url, merchant_code, consumer_key, consumer_secret):
        if not self._is_valid_amount(payment_request.amount):
            raise FailedPaymentException(f"Amount is less than the minimum transaction amount: UGX {PAYLEO_MIN_TRANSACTION_AMOUNT}")
        msisdn = self._clean_msisdn(payment_request.payer_msisdn)
        url = self._clean_url(url)
        narration = f"Payment request of {payment_request.amount}"
        transaction_id = self._get_transaction_id(payment_request.payment_id)
        payload = {
            "msisdn": f"{msisdn}",
            "amount": f"{payment_request.amount}",
            "merchantCode": merchant_code,
            "transactionId": transaction_id,
            "consumerKey": consumer_key,
            "narration": narration
        }
        auth_signature = self._get_auth_signature(url, consumer_secret, payload)
        payload["auth_signature"] = auth_signature
        super().__init__(payload)

    @staticmethod
    def _get_auth_signature(url, consumer_secret,payload):
        auth_signature_input = f"{url}&{payload['msisdn']}&{payload['amount']}&{payload['merchantCode']}&{payload['transactionId']}&{payload['narration']}"
        auth_signature = hmac.new(consumer_secret.encode("utf-8"), auth_signature_input.encode('utf-8'),
                                  hashlib.sha256).hexdigest()
        return auth_signature

    @staticmethod
    def _is_valid_amount(amount):
        amount = int(amount)
        if amount < PAYLEO_MIN_TRANSACTION_AMOUNT:
            return False
        return True

    @staticmethod
    def _clean_msisdn(msisdn):
        return str(msisdn).lstrip("+")

    @staticmethod
    def _clean_url(url):
        return url.rstrip("/")

    @staticmethod
    def _get_transaction_id(payment_id):
        pad_len = PAYLEO_CLIENT_TRANSACTION_ID_LENGTH - len(str(payment_id))
        pad_char = '0'
        if pad_len > 0:
            return pad_char * pad_len + str(payment_id)
        return payment_id
