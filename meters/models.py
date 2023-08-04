import json

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.serializers import serialize

from vendor_api import register_meter
from meter_vendors.models import MeterVendor
from users.filters import MANAGERS
from core.services.payment import request_payment

User = get_user_model()


class MeterQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_super_admin() or user.is_admin():
            return self.all()
        return self.filter(manager=user)


class Meter(models.Model):
    meter_number = models.CharField(max_length=11, unique=True)
    vendor = models.ForeignKey(MeterVendor, on_delete=models.PROTECT, related_name="meters")
    manager = models.ForeignKey(User, on_delete=models.PROTECT, default=User.objects.get_default_manager,
                                limit_choices_to=MANAGERS, related_name="meters")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = MeterQuerySet.as_manager()

    class Meta:
        ordering = ["manager"]

    @property
    def vendor_name(self):
        return self.vendor.name

    @property
    def manager_full_name(self):
        if self.manager:
            return self.manager.full_name

    @property
    def manager_unit_price(self):
        return 1000  # TODO: Update and use manager unit price instead hard-wired value

    @property
    def manager_phone_no(self):
        return self.manager.phone_no

    def recharge(self, recharge_amount, applied_unit_price):
        """ Get a recharge token for a meter"""
        from recharge_tokens.models import RechargeTokenOrder as Order
        order = Order.objects.place_order(recharge_amount, applied_unit_price, self)
        payer_phone_no = self.manager_phone_no
        external_payment_id = request_payment(order.payment_pk, order.payment_amount, payer_phone_no)
        order.update_payment_external_id(external_payment_id)
        return order

    def register(self):
        return register_meter(self)

    def deactivate(self):
        self.is_active = False
        self.save()

    def activate(self):
        self.is_active = True
        self.save()

    def get_due_fees(self):
        days_in_a_month = 30
        now = timezone.now()
        last_paid_at = self.created_at  # Default the last paid date to the creation date of the meter
        if hasattr(self, "metermonthlyfeepaymentlog"):  # Meter has an entry in the MeterMonthlyFeeLog
            last_paid_at = self.metermonthlyfeepaymentlog.last_paid_at
        months_due = (now - last_paid_at).days // days_in_a_month
        return months_due * settings.LEGIT_SYSTEMS_METER_MONTHLY_FLAT_FEE

    def as_json(self):
        return json.dumps(json.loads(serialize("json", [self])[1:-1])["fields"])

    def get_recharge_initial(self):
        return json.dumps({
            "meter_number": self.meter_number,
            "applied_unit_price": self.manager_unit_price,
            "due_fees": self.get_due_fees()
        })

    def __str__(self):
        return self.meter_number


class MeterMonthlyFeePaymentLog(models.Model):
    meter = models.OneToOneField(Meter, on_delete=models.PROTECT)
    last_paid_at = models.DateTimeField()

    def __str__(self):
        return self.meter
