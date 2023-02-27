import uuid

from vendor_api.vendors.api_factory import MeterVendorAPIFactoryImpl


class MeterCustomer:
    def __init__(self, meter_customer):
        self.__meter_customer = meter_customer

    @property
    def first_name(self):
        return self.__meter_customer.first_name

    @property
    def last_name(self):
        return self.__meter_customer.last_name

    @property
    def full_name(self):
        return self.__meter_customer.full_name

    @property
    def email(self):
        return self.__meter_customer.email

    @property
    def address(self):
        return self.__meter_customer.address

    @property
    def id(self):
        return "%d_%s" % (self.__meter_customer.id, str(uuid.uuid4()))

    @property
    def phone_no(self):
        return self.__meter_customer.phone_no


class Meter:
    owner = None

    def __init__(self, meter):
        self.__meter = meter
        self.owner = MeterCustomer(meter.manager)

    @property
    def meter_no(self):
        return self.__meter.meter_no

    def register(self):
        meter_vendor_api = self.__get_vendor_api()
        return meter_vendor_api.register_meter(self)

    def recharge(self, num_of_units):
        meter_vendor_api = self.__get_vendor_api()
        return meter_vendor_api.recharge_meter(self, num_of_units)

    def __get_vendor_api(self):
        meter_vendor_name = self.__meter.manufacturer_name
        meter_vendor_api = MeterVendorAPIFactoryImpl.get(meter_vendor_name)
        return meter_vendor_api


class PriceCategory:
    """
    Implement this model and the respective payload
    """
    pass


class RechargeToken:

    def __init__(self, token_no, num_of_units, unit):
        self.token_no = token_no
        self.num_of_units = num_of_units
        self.unit = unit

