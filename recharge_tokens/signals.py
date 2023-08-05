from django.dispatch import receiver
from django.template.loader import render_to_string

from payments.models import Payment
from payments.signals import payment_successful, payment_failed


def send_successful_recharge_sms(order):
    context = {
        "name": order.manager.first_name,
        "amount": order.recharge_amount,
        "token_no": order.token_no,
        "meter_no": order.meter.meter_number,
        "num_of_units": order.num_of_units,
        "applied_fees": order.applied_fees,
        "transaction_id": order.payment.external_id or order.payment.id
    }
    message = render_to_string("recharge_tokens/sms/successful_recharge.txt", context=context)
    order.manager.notify_by_sms(subject="Payment Received", message=message)


def send_failed_payment_sms(payment, meter):
    context = {
        "amount": payment.amount,
        "meter_no": meter.meter_number,
        "transaction_id": payment.external_id or payment.id
    }
    message = render_to_string("recharge_tokens/sms/failed_payment.txt", context=context)
    meter.manager.notify_by_sms(subject="Payment Failed", message=message)


def send_failed_token_generation_sms(order):
    context = {
        "name": order.manager.first_name,
        "amount": order.recharge_amount,
        "meter_no": order.meter.meter_number,
        "order_id": order.id
    }
    message = render_to_string("recharge_tokens/sms/failed_token_generation.txt", context=context)
    order.manager.notify_by_sms(subject="Payment Received", message=message)


@receiver(payment_successful, sender=Payment)
def deliver_order(sender, payment, **kwargs):
    recharge_token_order = payment.deliver_order()
    if recharge_token_order.is_delivered():
        send_successful_recharge_sms(recharge_token_order)
    else:
        # Payment was received but somehow, the order wasn't delivered
        send_failed_token_generation_sms(recharge_token_order)


@receiver(payment_failed, sender=Payment)
def notify_manager(sender, payment, meter, **kwargs):
    send_failed_payment_sms(payment, meter)
