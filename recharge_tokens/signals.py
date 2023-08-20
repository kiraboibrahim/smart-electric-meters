import logging
from django.dispatch import receiver
from django.template.loader import render_to_string

from core.services.notification.backends.exceptions import FailedSMSDeliveryException
from payments.models import Payment
from payments.signals import payment_successful, payment_failed

logger = logging.getLogger(__name__)


def send_successful_recharge_sms(order):
    context = {
        "name": order.customer_first_name,
        "amount": order.recharge_amount,
        "token_no": order.token_no,
        "meter_no": order.customer_meter_number,
        "num_of_units": order.num_of_units,
        "applied_fees": order.applied_fees,
        "transaction_id": order.transaction_id
    }
    message = render_to_string("recharge_tokens/sms/successful_recharge.txt", context=context)
    try:
        order.notify_customer(subject="Payment Received", message=message)
    except FailedSMSDeliveryException as exc:
        logger.exception("Failed to deliver message", exc_info=exc)
        pass


def send_failed_payment_sms(order):
    context = {
        "amount": order.payment_amount,
        "meter_no": order.customer_meter_number,
        "transaction_id": order.transaction_id
    }
    message = render_to_string("recharge_tokens/sms/failed_payment.txt", context=context)
    try:
        order.notify_customer(subject="Payment Failed", message=message)
    except FailedSMSDeliveryException as exc:
        logger.exception("Failed to deliver message", exc_info=exc)
        pass


def send_failed_token_generation_sms(order):
    context = {
        "name": order.customer_first_name,
        "amount": order.recharge_amount,
        "meter_no": order.customer_meter_number,
        "order_id": order.id
    }
    message = render_to_string("recharge_tokens/sms/failed_token_generation.txt", context=context)
    try:
        order.notify_customer(subject="Payment Received", message=message)
    except FailedSMSDeliveryException as exc:
        logger.exception("Failed to deliver message", exc_info=exc)
        pass


@receiver(payment_successful, sender=Payment)
def get_recharge_token(sender, payment, associated_order, **kwargs):
    associated_order.deliver()
    if associated_order.is_delivered():
        send_successful_recharge_sms(associated_order)
    else:
        # The payment was successful, but somehow, the token wasn't received from the vendor API
        send_failed_token_generation_sms(associated_order)


@receiver(payment_failed, sender=Payment)
def notify_manger(sender, payment, associated_order, **kwargs):
    send_failed_payment_sms(associated_order)
