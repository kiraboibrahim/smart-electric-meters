import requests
import abc
import uuid

from django.conf import settings
from meter.utils import create_meter_manufacturer_hash

meter_api_classes = {}

def register(cls):
    """
    This function registers all meter api classes so that the factory method can easily instantiate the meter api classes
    """
    meter_manufacturer_hash = create_meter_manufacturer_hash(cls.__name__)
    meter_api_classes[meter_manufacturer_hash] = cls
    return cls


class MeterAPI(abc.ABC):

    @abc.abstractmethod
    def get_token(self, payload):
        raise NotImplementedError

    @abc.abstractmethod
    def register_meter_customer(self, payload):
        raise NotImplementedError

    @abc.abstractmethod
    def register_price_category(self, payload):
        raise NotImplementedError
    

class MeterAPIFactory(abc.ABC):

    @abc.abstractmethod
    def create_api(self, api_name: str):
        raise NotImplementedError


class MeterAPIFactoryImpl(MeterAPIFactory):
    
    @classmethod
    def create_api(cls, company_name: str):
        meter_api_class = meter_api_classes.get(create_meter_manufacturer_hash(company_name), None)
        if meter_api_class is not None:
            return meter_api_class()
        raise Exception("Meter API for %s has not been added yet." %(company_name))


class MeterAPIException(Exception):
    def __init__(self, status_code: int, message: str = ""):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return "%d: %s" %(self.status_code, self.message)

    
@register
class StronPower(MeterAPI):

    BASE_URL = "http://www.server-api.stronpower.com/api"
    
    def __init__(self):
        self.username = settings.STRON_API_USERNAME
        self.password = settings.STRON_API_PWD
        self.company_name = "LEGIT-SYSTEMS"
        
        # Every payload should have username and password fields
        self.payload = {
            
            "UserName": self.username,
            "PassWord": self.password,
            "CompanyName": self.company_name,
        }

    def register_meter_customer(self, payload) -> bool:
        random_customer_id = str(uuid.uuid4())
        payload = {
            
            "AccountID": "API-ID",
            "CustomerID": random_customer_id,
            "CustomerName": payload.meter_owner_name,
            "CustomerAddress": payload.meter_owner_address,
            "CustomerPhone": payload.meter_owner_phone_no,
            "CustomerEmail": payload.meter_owner_email,
            "PriceCategories": payload.meter_price_category,
            "SalesStationID": "API-STATION",
            "MeterID": payload.meter_no,
            "MeterType": 0
        }

        payload.update(self.payload)

        response = self.request("NewCustomer", payload)

        response_text = response.text.strip('"')
        if response_text != "true":
            self.raise_exception(400, "Bad request")

        return True

    def register_price_category(self, payload) -> bool:

        payload = {
    
            "PRICE_ID": payload.id,
            "Categories": payload.label,
            "PRICE": payload.price_ugx,
            "VAT_RATE": 0.0,
            "PRICE_UNIT": "UGX",
            "REMARK": "Registering Price Category"
        }
        # Set username and password 
        payload.update(self.payload)
        
        response = self.request("NewPrice", payload)
            
        response_text = response.text.strip('"')
        if response_text != "true":
            self.raise_exception(400, "Bad request")
            
        return True
            
    def get_token(self, payload) -> dict:
        payload = {

            "MeterID": payload.meter_no,
            "is_vend_by_unit": "true",
            "Amount": "%s" %(str(payload.amount))
        }
        # Upadate with the username, password, and company name
        payload.update(self.payload)
            
        response = self.request("VendingMeter", payload)
        response = response.json()
        if response == []:
            # It is an empty response, some error have been triggered but the api doesnot give helpful info
            self.raise_exception(400, "Bad request- No token received from meter API")

        return {
                 "token": response[0]["Token"],
                 "created_at": response[0]["Gen_time"],
                 "num_of_units": response[0]["Total_unit"],
                 "unit": response[0]["Unit"],
               }
    
    def raise_exception(self, code: int, message: str):
        raise MeterAPIException(code, message)


    def request(self, endpoint: str, payload):
        response = requests.post("%s/%s" %(StronPower.BASE_URL, endpoint), json=payload)
        if response.status_code != 200:
            self.raise_exception(response.status_code, response.text)

        return response

