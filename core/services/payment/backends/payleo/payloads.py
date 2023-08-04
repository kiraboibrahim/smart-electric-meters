import hmac
import hashlib


class PaymentRequestPayload(dict):

    def __init__(self, payment_request, url, merchant_code, consumer_key, consumer_secret):
        msisdn = str(payment_request.payer_msisdn).lstrip("+")
        url = url.rstrip("/")
        narration = f"Payment request of {payment_request.amount}"
        transaction_id = self._payment_id_to_transaction_id(payment_request.payment_id)
        payload = {
            "msisdn": f"{msisdn}",
            "amount": f"{payment_request.amount}",
            "merchantCode": merchant_code,
            "transactionId": transaction_id,
            "consumerKey": consumer_key,
            "narration": narration
        }
        auth_signature_input = f"{url}&{payload['msisdn']}&{payload['amount']}&{merchant_code}&{payload['transactionId']}&{payload['narration']}"
        auth_signature = hmac.new(consumer_secret.encode("utf-8"), auth_signature_input.encode('utf-8'),
                                  hashlib.sha256).hexdigest()
        payload["auth_signature"] = auth_signature
        super().__init__(payload)

    @staticmethod
    def _payment_id_to_transaction_id(payment_id):
        # Transform the payment_id to meet the expected requirements of transactionId in the payload
        # The transactionId should be 15 chars long
        pad_len = 15 - len(str(payment_id))
        if pad_len > 0:
            return '0'*pad_len + str(payment_id)
        return payment_id
