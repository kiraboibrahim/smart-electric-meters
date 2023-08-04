import uuid

from vendor_api.vendors import factory as meter_vendor_api_factory


class Manager:
    def __init__(self, manager):
        self._manager = manager

    @property
    def name(self):
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

    def __str__(self):
        return self.phone_no


class Meter:
    def __init__(self, meter):
        self._meter = meter
        self._manager = Manager(meter.manager)
        self._vendor_api = self._get_vendor_api()

    @property
    def meter_no(self):
        return self._meter.meter_number

    @property
    def manager_name(self):
        return self._manager.name

    @property
    def manager_email(self):
        return self._manager.email

    @property
    def manager_address(self):
        return self._manager.address

    @property
    def manager_id(self):
        return self._manager.id

    @property
    def manager_phone_no(self):
        return self._manager.phone_no

    def register(self):
        return self._vendor_api.register_meter(self)

    def recharge(self, num_of_units):
        return self._vendor_api.recharge_meter(self, num_of_units)

    def _get_vendor_api(self):
        meter_vendor_name = self._meter.vendor_name
        return meter_vendor_api_factory.get_api(meter_vendor_name)

    def __str__(self):
        return self.meter_no
