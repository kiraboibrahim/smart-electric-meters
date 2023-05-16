import re
import import_string

from vendor_api.vendors.base import MeterVendorAPIFactory
from vendor_api.vendors.exceptions import MeterVendorAPINotFoundException


class MeterVendorAPIFactoryImpl(MeterVendorAPIFactory):

    def get_api(self, vendor_name):
        """
            Each meters vendor has their own module under vendor directory
            All vendor module names are devoid of non ascii characters, spaces are replaced with underscore '_'
        """
        vendor_name = self._clean_vendor_name(vendor_name)
        try:
            vendor_api = import_string("vendor_api.vendors.%s.api:Vendor" % vendor_name)
        except ImportError:
            raise MeterVendorAPINotFoundException()
        return vendor_api()

    @staticmethod
    def _clean_vendor_name(vendor_name):
        vendor_name = vendor_name.encode("ascii", "ignore").strip().lower()
        return re.sub(r"\s+", "_", vendor_name)

factory = MeterVendorAPIFactoryImpl()
