import random
import string

from vendor_api.models import Meter
from vendor_api.vendors.base import MeterVendorAPI


class VendorAPI(MeterVendorAPI):

    def register_meter(self, meter: Meter) -> bool:
        return True

    def recharge_meter(self, meter: Meter, num_of_units: int) -> str:
        token_no = self._get_token_no()
        return token_no

    @staticmethod
    def _get_token_no(token_length: int = 20) -> str:
        return "".join([random.choice(string.digits) for _ in range(token_length)])
