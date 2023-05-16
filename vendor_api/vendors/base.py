import abc


class MeterVendorAPI(abc.ABC):

    @abc.abstractmethod
    def recharge_meter(self, meter, num_of_units):
        raise NotImplementedError

    @abc.abstractmethod
    def register_meter(self, meter) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def register_price_category(self, price_category) -> bool:
        raise NotImplementedError


class MeterVendorAPIFactory(abc.ABC):

    @abc.abstractmethod
    def get_api(self, vendor_name: str):
        raise NotImplementedError
