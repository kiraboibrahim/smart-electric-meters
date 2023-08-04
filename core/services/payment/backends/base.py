import abc


class PaymentRequest:
    def __init__(self, payment_id, payer_msisdn, amount):
        self.payer_msisdn = payer_msisdn
        self.amount = amount
        self.payment_id = payment_id


class PaymentBackend(abc.ABC):

    @abc.abstractmethod
    def request_payment(self, payment_request: PaymentRequest):
        raise NotImplementedError
