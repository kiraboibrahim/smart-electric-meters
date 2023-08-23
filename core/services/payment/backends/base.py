import abc


class PaymentRequest:
    def __init__(self, payment_id, amount, payer_msisdn):
        self.payer_msisdn = f"{payer_msisdn}"
        self.amount = f"{amount}"
        self.payment_id = f"{payment_id}"


class PaymentBackend(abc.ABC):

    @abc.abstractmethod
    def request_payment(self, payment_request: PaymentRequest):
        raise NotImplementedError
