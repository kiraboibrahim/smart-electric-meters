import re


def clean_meter_vendor_name(meter_vendor_name):
    meter_vendor_name = meter_vendor_name.encode("ascii", "ignore").decode().strip().lower()
    return re.sub(r"\s+", "_", meter_vendor_name)
