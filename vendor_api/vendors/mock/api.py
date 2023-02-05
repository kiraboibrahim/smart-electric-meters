import random
import string

from vendor_api.models import Meter, PriceCategory, RechargeToken
from vendor_api.vendors.base import MeterVendorAPI


class Vendor(MeterVendorAPI):

    def register_price_category(self, price_category: PriceCategory) -> bool:
        return True

    def register_meter(self, meter: Meter) -> bool:
        return True

    def recharge_meter(self, meter: Meter, num_of_units: int) -> RechargeToken:
        token_number = self._generate_token_number()
        recharge_token = RechargeToken()
        recharge_token.token_no = token_number
        recharge_token.num_of_units = num_of_units
        recharge_token.unit = "KwH"
        return recharge_token

    @staticmethod
    def _generate_token_number(token_length: int = 20) -> int:
        return int("".join([random.choice(string.digits) for _ in range(token_length)]))
