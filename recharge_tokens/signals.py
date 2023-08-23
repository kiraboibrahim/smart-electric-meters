import logging
from django.dispatch import receiver
from django.template.loader import render_to_string

from core.services.notification import send_notification
from core.services.notification.strategies import BY_SMS
from core.services.notification.backends.exceptions import FailedSMSDeliveryException
from payments.models import Payment
from payments.signals import payment_successful, payment_failed

logger = logging.getLogger(__name__)


def send_successful_recharge_sms(payment, order):
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
        send_notification([f"{payment.payer_phone_no}"], subject="Payment Received", message=message,
                          notification_strategy=BY_SMS)
    except FailedSMSDeliveryException as exc:
        logger.exception(f"Failed to deliver message to {payment.payer_phone_no}", exc_info=exc)


def send_failed_payment_sms(payment, order):
    context = {
        "amount": order.payment_amount,
        "meter_no": order.customer_meter_number,
        "transaction_id": order.transaction_id
    }
    message = render_to_string("recharge_tokens/sms/failed_payment.txt", context=context)
    try:
        send_notification([f"{payment.payer_phone_no}"], subject="Payment Failed", message=message,
                          notification_strategy=BY_SMS)
    except FailedSMSDeliveryException as exc:
        logger.exception(f"Failed to deliver message to {payment.payer_phone_no}", exc_info=exc)


def send_failed_token_generation_sms(payment, order):
    context = {
        "name": order.customer_first_name,
        "amount": order.recharge_amount,
        "meter_no": order.customer_meter_number,
        "order_id": order.id
    }
    message = render_to_string("recharge_tokens/sms/failed_token_generation.txt", context=context)
    try:
        send_notification([f"{payment.payer_phone_no}"], subject="Payment Received", message=message,
                          notification_strategy=BY_SMS)
    except FailedSMSDeliveryException as exc:
        logger.exception(f"Failed to deliver message to {payment.payer_phone_no}", exc_info=exc)


@receiver(payment_successful, sender=Payment)
def get_recharge_token(sender, payment, **kwargs):
    payment.order.deliver()  # Deliver the order to which the payment is attached
    if payment.order.is_delivered():
        send_successful_recharge_sms(payment, payment.order)
    else:
        # The payment was successful, but somehow, the token wasn't received from the vendor API
        send_failed_token_generation_sms(payment, payment.order)


@receiver(payment_failed, sender=Payment)
def notify_payer(sender, payment, **kwargs):
    send_failed_payment_sms(payment, payment.order)
