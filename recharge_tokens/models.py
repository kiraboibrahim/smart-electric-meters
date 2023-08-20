from django.db import models
from django.contrib.auth import get_user_model

import meters.models
from vendor_api import recharge_meter
from payments.models import Payment
from core.services.payment import request_payment
from core.services.notification.strategies import BY_SMS

User = get_user_model()


class RechargeTokenOrderQueryset(models.QuerySet):

    def for_user(self, user):
        if user.is_super_admin() or user.is_admin():
            return self.all()
        return self.filter(meter__manager=user)


class RechargeTokenOrderManager(models.Manager):

    def place_order(self, recharge_amount, applied_unit_price, meter):
        applied_fees = meter.due_fees
        amount_to_be_paid = recharge_amount + applied_fees  # client has to pay the fees too
        payment = Payment.objects.create_pending_payment(amount=amount_to_be_paid)
        return self.create(meter=meter, payment=payment, applied_unit_price=applied_unit_price,
                           applied_fees=applied_fees, recharge_amount=recharge_amount)


class RechargeTokenOrder(models.Model):
    meter = models.ForeignKey(meters.models.Meter, on_delete=models.CASCADE)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name="order")
    token_no = models.CharField(null=True, max_length=255)
    applied_fees = models.PositiveIntegerField()
    recharge_amount = models.PositiveIntegerField()
    applied_unit_price = models.PositiveIntegerField()
    placed_at = models.DateTimeField(auto_now_add=True)

    objects = RechargeTokenOrderManager.from_queryset(RechargeTokenOrderQueryset)()

    class Meta:
        ordering = ("-placed_at", )

    @property
    def customer(self):
        return self.meter.manager

    @property
    def customer_first_name(self):
        return self.customer.first_name

    @property
    def customer_meter_number(self):
        return self.meter.meter_number

    @property
    def meter_no(self):
        return self.meter.meter_number

    @property
    def num_of_units(self):
        net_recharge_amount = self.payment.amount - self.applied_fees
        return round(net_recharge_amount / self.applied_unit_price, 1)

    @property
    def payment_amount(self):
        return self.payment.amount

    @property
    def transaction_id(self):
        return self.payment.id

    @property
    def external_transaction_id(self):
        """ The ID returned by the Payment Service Provider. This can be used to resolve problems between the client
        and the Payment Service Provider."""
        return self.payment.external_id

    def pay(self, payer_phone_no=None):
        payer_phone_no = self.customer.phone_no if payer_phone_no is None else payer_phone_no
        external_payment_id = request_payment(self.transaction_id, self.payment_amount, payer_phone_no)
        self.set_external_payment_id(external_payment_id)

    def deliver(self):
        """ Get recharge token from vendor"""
        if self.payment.is_successful() and not self.is_delivered():
            self.token_no = recharge_meter(self.meter, self.num_of_units)
            self.save()

    def get_status_label(self):
        if self.payment.is_pending():
            return "Pending Payment"
        elif self.payment.is_failed():
            return "Failed Payment"
        elif self.payment.is_successful() and not self.is_delivered():
            return "Pending Delivery"
        elif self.payment.is_successful() and self.is_delivered():
            return "Delivered"

    def is_delivered(self):
        return self.token_no is not None

    def notify_customer(self, subject, message, strategy=BY_SMS):
        self.customer.notify_by_sms(subject, message) if strategy is BY_SMS else self.customer.notify_by_email(subject, message)

    def set_external_payment_id(self, external_id):
        self.payment.set_external_id(external_id)

    def __str__(self):
        return f"{self.id}"
