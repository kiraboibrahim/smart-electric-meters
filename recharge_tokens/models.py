from django.db import models
from django.contrib.auth import get_user_model

import meters.models
from vendor_api import recharge_meter
from payments.models import Payment

User = get_user_model()


class RechargeTokenOrderQueryset(models.QuerySet):

    def for_user(self, user):
        if user.is_manager():
            return self.filter(meter__manager=user)
        return self.all()


class RechargeTokenOrderManager(models.Manager):

    def place_order(self, recharge_amount, applied_unit_price, meter):
        applied_fees = meter.get_due_fees()
        amount_to_be_paid = recharge_amount + applied_fees  # client pays the fees too
        payment = Payment.objects.create_pending_payment(amount=amount_to_be_paid)
        return self.create(meter=meter, payment=payment, applied_unit_price=applied_unit_price,
                           applied_fees=applied_fees, recharge_amount=recharge_amount)


class RechargeTokenOrder(models.Model):
    meter = models.ForeignKey(meters.models.Meter, on_delete=models.PROTECT)
    payment = models.OneToOneField(Payment, on_delete=models.PROTECT, related_name="order")
    token_no = models.CharField(null=True, max_length=255)
    applied_fees = models.PositiveIntegerField()
    recharge_amount = models.PositiveIntegerField()
    applied_unit_price = models.PositiveIntegerField()
    placed_at = models.DateTimeField(auto_now_add=True)

    objects = RechargeTokenOrderManager.from_queryset(RechargeTokenOrderQueryset)()

    class Meta:
        ordering = ("-placed_at", )

    @property
    def num_of_units(self):
        net_recharge_amount = self.payment.amount - self.applied_fees
        return round(net_recharge_amount/self.applied_unit_price, 1)

    @property
    def payment_pk(self):
        return self.payment.id

    @property
    def payment_amount(self):
        return self.payment.amount

    @property
    def meter_no(self):
        return self.meter.meter_number

    @property
    def manager(self):
        return self.meter.manager

    def is_delivered(self):
        # Payment was successful and token was also delivered
        return self.token_no is not None

    def is_pending(self):
        return self.payment.is_pending()

    def deliver(self):
        if not self.is_delivered():
            self.token_no = recharge_meter(self.meter, self.num_of_units)
            self.save()
        return self

    def update_payment_external_id(self, external_id):
        self.payment.external_id = external_id
        self.payment.save()

    def __str__(self):
        return self.id
