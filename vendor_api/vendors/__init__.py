import import_string

from vendor_api.vendors.base import MeterVendorAPIFactory
from vendor_api.vendors.exceptions import MeterVendorAPINotFoundException

from .utils import clean_meter_vendor_name


class MeterVendorAPIFactoryImpl(MeterVendorAPIFactory):

    def get_api(self, meter_vendor_name):
        """
            Each meters vendor has their own module under vendors directory, Before integrating another vendor,
            please use the clean_meter_vendor_name() function to get the expected module full_name
        """
        meter_vendor_name = clean_meter_vendor_name(meter_vendor_name)
        MeterVendorAPI = import_string(f"vendor_api.vendors.{meter_vendor_name}.api:VendorAPI", silent=True)
        if MeterVendorAPI is None:
            raise MeterVendorAPINotFoundException()
        return MeterVendorAPI()

    def is_vendor_api_available(self, meter_vendor_name):
        meter_vendor_name = clean_meter_vendor_name(meter_vendor_name)
        MeterVendorAPI = import_string(f"vendor_api.vendors.{meter_vendor_name}.api:VendorAPI", silent=True)
        if MeterVendorAPI is None:
            return False
        return True


factory = MeterVendorAPIFactoryImpl()

