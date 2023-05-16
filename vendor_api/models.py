import uuid

from vendor_api.vendors.api_factory import factory


class Manager:
    def __init__(self, manager):
        self._manager = manager

    @property
    def first_name(self):
        return self._manager.first_name

    @property
    def last_name(self):
        return self._manager.last_name

    @property
    def full_name(self):
        return self._manager.full_name

    @property
    def email(self):
        return self._manager.email

    @property
    def address(self):
        return self._manager.address

    @property
    def id(self):
        return "%d_%s" % (self._manager.id, str(uuid.uuid4()))

    @property
    def phone_no(self):
        return self._manager.phone_no


class Meter:
    def __init__(self, meter):
        self._meter = meter
        self._manager = Manager(meter.manager)

    @property
    def meter_no(self):
        return self._meter.meter_no

    @property
    def manager_last_name(self):
        return self._manager.last_name

    @property
    def manager_full_name(self):
        return self._manager.full_name

    @property
    def manager_email(self):
        return self._manager.email

    @property
    def manager_id(self):
        return self._manager.id

    @property
    def manager_phone_no(self):
        return self._manager.phone_no

    def register(self):
        meter_vendor_api = self._get_vendor_api()
        return meter_vendor_api.register_meter(self)

    def recharge(self, num_of_units):
        meter_vendor_api = self._get_vendor_api()
        return meter_vendor_api.recharge_meter(self, num_of_units)

    def _get_vendor_api(self):
        meter_vendor_name = self._meter.manufacturer_name
        meter_vendor_api = factory.get_api(meter_vendor_name)
        return meter_vendor_api


class RechargeToken:

    def __init__(self, token_no, num_of_units, unit):
        self.token_no = token_no
        self.num_of_units = num_of_units
        self.unit = unit


class PriceCategory:
    """
    Implement this model and the respective payload
    """
    pass
