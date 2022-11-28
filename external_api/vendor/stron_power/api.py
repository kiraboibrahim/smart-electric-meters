import requests
import logging

from django.conf import settings

from external_api.vendor.base import MeterVendorAPI
from external_api.vendor.stron_power.payloads import RegisterMeterPayload, RechargeMeterPayload
from external_api.vendor.exceptions import MeterRegistrationException, EmptyTokenResponseException, \
    MeterVendorAPIException
from external_api.models import RechargeToken


logger = logging.getLogger(__name__)


class Vendor(MeterVendorAPI):

    BASE_URL = "http://www.server-api.stronpower.com/api"
    NAME = "LEGIT-SYSTEMS"

    def __init__(self):
        self.username = settings.STRON_POWER_USERNAME
        self.password = settings.STRON_POWER_PASSWORD

        self.auth_credentials = {
            "UserName": self.username,
            "PassWord": self.password,
            "CompanyName": self.NAME
        }

    def register_meter(self, meter):
        RegisterMeterPayload.meter = meter
        payload = RegisterMeterPayload.get()

        response = self.request("NewCustomer", payload)
        txt_response = response.text.strip('"')
        if txt_response != "true":
            raise MeterRegistrationException(response.status_code, txt_response)
        return True

    def recharge_meter(self, meter, num_of_units):
        RechargeMeterPayload.meter = meter
        RechargeMeterPayload.num_of_units = num_of_units
        payload = RechargeMeterPayload.get()

        response = self.request("VendingMeter", payload)
        try:
            response = response.json()[0]
        except IndexError as error:
            raise EmptyTokenResponseException(response.status_code)
        recharge_token = RechargeToken()
        recharge_token.token_no = response["Token"]
        recharge_token.num_of_units = response["Total_unit"]
        recharge_token.unit = response["Unit"]
        return recharge_token

    def register_price_category(self, price_category):
        raise NotImplementedError

    def request(self, endpoint, payload):
        url = "%s/%s" % (self.BASE_URL, endpoint)
        payload.update(self.auth_credentials)
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            raise MeterVendorAPIException(response.status_code, response.text)
        return response
