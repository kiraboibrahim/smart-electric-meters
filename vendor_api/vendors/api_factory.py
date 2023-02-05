import import_string

from vendor_api.vendors.base import MeterVendorAPIFactory
from vendor_api.vendors.exceptions import MeterVendorAPINotFoundException


class MeterVendorAPIFactoryImpl(MeterVendorAPIFactory):

    @classmethod
    def get(cls, vendor_name):
        """
            Each meters vendor has their own module under vendor directory
            All vendor module names are derived from the vendor names and must be in snake_case,
            no trailing or preceding spaces
        """
        vendor_name = vendor_name.lower().strip().replace(" ", "_")
        try:
            vendor_api_class = import_string("vendor_api.vendors.%s.api:Vendor" % vendor_name)
        except ImportError:
            raise MeterVendorAPINotFoundException()
        return vendor_api_class()
