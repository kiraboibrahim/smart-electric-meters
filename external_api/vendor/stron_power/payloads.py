from .settings import ACCOUNT_ID, SALES_STATION_ID, METER_PRICE_CATEGORY, METER_TYPE_ENERGY, VEND_BY_UNIT

from ..exceptions import MissingPayloadAttributeException


class RegisterMeterPayload:
    fields = {
        "MeterID": None,
        "MeterType": None,
        "AccountID": None,
        "SalesStationID": None,
        "CustomerID": None,
        "CustomerName": None,
        "CustomerAddress": None,
        "CustomerPhone": None,
        "CustomerEmail": None,
        "PriceCategories": None
    }
    meter = None
    meter_owner = None

    @classmethod
    def get(cls):
        if cls.meter is None:
            raise MissingPayloadAttributeException("You must specify a meter during meter registration")
        cls.meter_owner = cls.meter.owner

        cls.fields["MeterID"] = cls.meter.meter_no
        cls.fields["MeterType"] = METER_TYPE_ENERGY
        cls.fields["AccountID"] = ACCOUNT_ID
        cls.fields["SalesStationID"] = SALES_STATION_ID
        cls.fields["CustomerID"] = cls.meter_owner.id
        cls.fields["CustomerName"] = cls.meter_owner.full_name
        cls.fields["CustomerAddress"] = cls.meter_owner.address
        cls.fields["CustomerPhone"] = cls.meter_owner.phone_no
        cls.fields["CustomerEmail"] = cls.meter_owner.email
        cls.fields["PriceCategories"] = METER_PRICE_CATEGORY
        return cls.fields


class RechargeMeterPayload:
    fields = {
        "MeterID": None,
        "is_vend_by_unit": VEND_BY_UNIT,
        "Amount": None
    }
    meter = None
    num_of_units = 0

    @classmethod
    def get(cls):
        if cls.meter is None:
            raise MissingPayloadAttributeException("You must specify a meter when recharging")
        if cls.num_of_units <= 0:
            raise MissingPayloadAttributeException("The number of units should be greater than zero")
        cls.fields["MeterID"] = cls.meter.meter_no
        cls.fields["Amount"] = cls.num_of_units
        return cls.fields
