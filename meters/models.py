import json

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

from core.mixins import ModelDiffMixin
from vendor_api import register_meter
from meter_vendors.models import MeterVendor
from users.filters import MANAGERS

User = get_user_model()


class MeterMonthlyFeePaymentLog(models.Model):
    meter = models.OneToOneField("Meter", on_delete=models.PROTECT)
    last_paid_at = models.DateTimeField()

    def __str__(self):
        return self.meter


class MeterQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_super_admin() or user.is_admin():
            return self.all()
        return self.filter(manager=user)


class Meter(ModelDiffMixin, models.Model):
    meter_number = models.CharField(max_length=11, unique=True)
    vendor = models.ForeignKey(MeterVendor, on_delete=models.PROTECT, related_name="meters")
    manager = models.ForeignKey(User, on_delete=models.PROTECT, default=User.objects.get_default_manager,
                                limit_choices_to=MANAGERS, related_name="meters")
    is_active = models.BooleanField(default=True)
    # Keep track of previously registered vendors to avoid re-registration when meters are updated
    previous_vendor_registrations = models.ManyToManyField(MeterVendor, related_name="registered_meters")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = MeterQuerySet.as_manager()

    class Meta:
        ordering = ["meter_number"]

    @property
    def due_fees(self):
        days_in_a_month = 30
        now = timezone.now()
        # Default the last paid date to the creation date of the meter. This will be handy for meters that haven't made
        # a single payment. They will be charged with reference from the creation date
        last_paid_at = self.created_at
        if hasattr(self, "metermonthlyfeepaymentlog"):  # Meter has an entry in the MeterMonthlyFeeLog
            last_paid_at = self.metermonthlyfeepaymentlog.last_paid_at
        months_due = (now - last_paid_at).days // days_in_a_month
        return months_due * settings.LEGIT_SYSTEMS_METER_MONTHLY_FLAT_FEE

    @property
    def vendor_name(self):
        return self.vendor.name

    @property
    def manager_phone_no(self):
        return self.manager.phone_no

    @property
    def manager_full_name(self):
        if self.manager:
            return self.manager.full_name

    @property
    def manager_unit_price(self):
        return self.manager.unit_price

    @property
    def is_registered_with_vendor(self):
        return self.previous_vendor_registrations.all().filter(pk=self.vendor.id).exists()

    def recharge(self, recharge_amount, applied_unit_price):
        """ Get a recharge token for a meter"""
        from recharge_tokens.models import RechargeTokenOrder as Order
        order = Order.objects.place_order(recharge_amount, applied_unit_price, self)
        order.pay(payer_phone_no=self.manager_phone_no)
        return order

    def activate(self):
        self.is_active = True
        super().save(update_fields=["is_active"])

    def deactivate(self):
        self.is_active = False
        super().save(update_fields=["is_active"])

    def save(self, *args, **kwargs):
        skip_vendor_registration = kwargs.pop("skip_vendor_registration", False)
        changed_fields = self.changed_fields
        # Either a new meter or an updated meter(meter_number or vendor updated)
        is_new_meter = self.pk is None
        vendor_updated = "vendor" in changed_fields
        meter_number_updated = "meter_number" in changed_fields
        registration_required = (is_new_meter and not skip_vendor_registration) or meter_number_updated or (vendor_updated and not self.is_registered_with_vendor)
        super().save(*args, **kwargs)  # Save changes
        if meter_number_updated:
            # Because the meter number has been updated, all vendor registrations become invalid. However, this doesn't
            # handle cases where updates result into a meter number that was already registered sometime back. This
            # kind of validation should be handled by the Vendor API
            self.clear_previous_vendor_registrations()
        if registration_required:
            self.register()

    def clear_previous_vendor_registrations(self):
        self.previous_vendor_registrations.clear()

    def register(self):
        register_meter(self)
        self.add_vendors_to_previous_registrations(vendors=[self.vendor])

    def add_vendors_to_previous_registrations(self, vendors):
        self.previous_vendor_registrations.add(*vendors)

    def get_recharge_info(self):
        return json.dumps({"due_fees": self.due_fees, "meter_number": self.meter_number, "applied_unit_price": self.manager_unit_price})

    def as_json(self):
        from .serializers import MeterSerializer
        return json.dumps(MeterSerializer(instance=self).data)

    def update_last_payment_date(self, date):
        if hasattr(self, "metermonthlyfeepaymentlog"):  # Meter has an entry in the MeterMonthlyFeeLog
            self.metermonthlyfeepaymentlog.last_paid_at = date
            self.metermonthlyfeepaymentlog.save(update_fields=["last_paid_at"])
        else:
            MeterMonthlyFeePaymentLog.objects.create(meter=self, last_paid_at=date)

    def __str__(self):
        return self.meter_number

