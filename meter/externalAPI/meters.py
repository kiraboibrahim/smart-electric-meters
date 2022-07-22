import requests
import abc
import uuid

from django.conf import settings
from meter.utils import create_meter_manufacturer_hash

meter_APIs = {}

def register(cls):
    """
    This function registers all meter API classes so that the factory method can easily instantiate the meter APIs
    """
    API_id = create_meter_manufacturer_hash(cls.__name__)
    meter_APIs[API_id] = cls
    return cls

class Token:

    def set_token_no(self, token_no):
        self.token_no = token_no

    def set_num_of_units(self, num_of_units):
        self.num_of_units = num_of_units

    def set_unit(self, unit):
        self.unit = unit

class MeterAPI(abc.ABC):

    @abc.abstractmethod
    def get_token(self, token_spec):
        raise NotImplementedError

    @abc.abstractmethod
    def register_customer(self, customer):
        raise NotImplementedError

    @abc.abstractmethod
    def register_unit_price(self, unit_price):
        raise NotImplementedError
    

class MeterAPIFactory(abc.ABC):

    @abc.abstractmethod
    def get_API(self, manufacturer):
        raise NotImplementedError


class MeterAPIFactoryImpl(MeterAPIFactory):
    
    @classmethod
    def get_API(cls, manufacturer):
        API_id = create_meter_manufacturer_hash(manufacturer)
        meter_API = meter_APIs.get(API_id)()
        if meter_API is None:
            raise Exception("API for %s has not been implemented yet" %(manufacturer))
            
        return meter_API
        


class MeterAPIException(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return "%d: %s" %(self.status_code, self.message)

    
@register
class StronPower(MeterAPI):

    BASE_URL = "http://www.server-api.stronpower.com/api"
    ENERGY_METER = 0
    
    def __init__(self):
        self.client_name = "LEGIT-SYSTEMS"
        self.username = settings.STRON_API_USERNAME
        self.password = settings.STRON_API_PWD
        
        self.base_post_data = {
            "UserName": self.username,
            "PassWord": self.password,
            "CompanyName": self.client_name
        }

    
    def get_customer_endpoint_post_data(self, customer):
        post_data = {
            "AccountID": "API-ID",
            "SalesStationID": "API-STATION",
            "CustomerID": customer.get_id(),
            "CustomerName": customer.get_full_name(),
            "CustomerAddress": customer.get_address(),
            "CustomerPhone": customer.get_phone_no(),
            "CustomerEmail": customer.get_email(),
            "PriceCategories": customer.unit_price_label,
            "MeterID": customer.meter.meter_no,
            "MeterType": self.__class__.ENERGY_METER
        }
        return post_data
    
    def register_customer(self, customer):
        post_data = self.get_customer_endpoint_post_data(customer)
        post_data.update(self.base_post_data)

        API_response = self.request("NewCustomer", post_data)

        customer_registered = API_response.text.strip('"')
        if customer_registered != "true":
            self.raise_exception(400, "Customer registration failed")

        return True

    def get_unit_price_endpoint_post_data(self, unit_price):

        post_data = {
            "PRICE_ID": unit_price.id,
            "Categories": unit_price.label,
            "PRICE": unit_price.price,
            "VAT_RATE": 0.0,
            "PRICE_UNIT": "UGX",
            "REMARK": "Unit Price"
        }
        return post_data

    
    def register_unit_price(self, unit_price):
        post_data = self.get_unit_price_endpoint_post_data(unit_price)
        post_data.update(self.base_post_data)
        
        API_response = self.request("NewPrice", post_data)
            
        unit_price_registered = API_response.text.strip('"')
        if unit_price_registered != "true":
            self.raise_exception(400, "Unit price registration failed")
            
        return True

    def get_token_endpoint_post_data(self, token_spec):
        post_data = {
            "MeterID": token_spec.get_meter_no(),
            "is_vend_by_unit": "true",
            "Amount": "%s" %(str(token_spec.num_of_units))
        }
        return post_data

    def get_token(self, token_spec):
        post_data = self.get_token_endpoint_post_data(token_spec)
        post_data.update(self.base_post_data)
            
        API_response = self.request("VendingMeter", post_data)
        try:
            generated_token_from_API = API_response.json()[0]

            token = Token()
            token.set_token_no(generated_token_from_API["Token"])
            token.set_num_of_units(generated_token_from_API["Total_unit"])
            token.set_unit(generated_token_from_API["Unit"])

            return token
    
        except IndexError as e:
            self.raise_exception(400, "No token received from meter API")
            
    def raise_exception(self, status_code, message):
        raise MeterAPIException(status_code, message)


    def request(self, endpoint, post_data):
        API_response = requests.post("%s/%s" %(self.__class__.BASE_URL, endpoint), json=post_data)
        if API_response.status_code != 200:
            self.raise_exception(API_response.status_code, API_response.text)

        return API_response

