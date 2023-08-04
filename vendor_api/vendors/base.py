import abc


class MeterVendorAPI(abc.ABC):

    @abc.abstractmethod
    def recharge_meter(self, meter, num_of_units) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def register_meter(self, meter) -> bool:
        raise NotImplementedError


class MeterVendorAPIFactory(abc.ABC):

    @abc.abstractmethod
    def get_api(self, vendor_name: str) -> MeterVendorAPI:
        raise NotImplementedError
