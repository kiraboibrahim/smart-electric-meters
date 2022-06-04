from twilio.rest import Client
import requests
import base64
import time
import json
import abc
import os
import uuid

from django.conf import settings

from meter.utils import create_meter_manufacturer_hash

        
class MTNMobileMoneyException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code # Status code returned by MTNMoMo api
        self.message = message  # A description message attached to elucidate the status code
        super().__init__(self.message) # Call Exception class Constructor

    def __str__(self):
        return "%s - %s" %(str(self.status_code), self.message)

    
class AirtelMoneyException(MTNMobileMoneyException):
    def __init__(self, status_code: int, message: str):
        super.__init__(status_code, message)
        
    

class StronPowerException(Exception):
    def __init__(self, status_code: int, message: str = ""):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return "%d: %s" %(self.status_code, self.message)

        

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

    
    
class MobileMoneyAPIFactory(abc.ABC):

    @abc.abstractmethod
    def create_api(self, api_name: str):
        raise NotImplementedError
    

class MobileMoneyAPI(abc.ABC):
    
    @abc.abstractmethod
    def debit_funds(self, payload):
        raise NotImplementedError

    @abc.abstractmethod
    def get_transaction_state(self, transaction_reference):
        raise NotImplementedError


class MobileMoneyAPIFactoryImpl(MeterAPIFactory):

    @classmethod
    def create_api(self, api_name: str):
        if api_name.lower() == "airtel":
            return AirtelMoney()
        elif api_name.lower() == "mtn":
            return MTNMobileMoney()
        else:
            return None

        
class AirtelMoney(MobileMoneyAPI):

    def __init__(self):
        pass

    def debit_funds(self, payload):
        raise NotImplementedError

    def get_transaction_state(self, transaction_reference):
        raise NotImplementedError
    
    
class MTNMobileMoney(MobileMoneyAPI):
    # The collection service endpoint
    BASE_URL = "https://sandbox.momodeveloper.mtn.com/collection"
    # These are descriptions of the error codes returned as shown in the mtnmomo documentation:
    # https://momodeveloper.mtn.com/api-documentation/common-error/
    # The error codes below are all in the generic context except for the 500 error code which
    # is interpreted in the requesttopay endpoint context (I am only using requesttopay, no need to bother
    # with generic context though it may apply in certain scenarios)
    
    ERRORS   = {
        409 : "Duplicated Reference Id. Cannot create new resource.",
        404 : "Reference Id not found. Requested resource does not exist.",
        400 : "Bad request. Request does not follow the specification.",
        401 : "Authentication failed. Credentials not valid.",
        403 : "Authorization failed. IP address not allowed to transact.",
        500 : "Payer not found. Account holder not registered. or Payee cannot recieve funds due to... ie transfer limit exceeded or Internal Server Error.",
        503 : "Service temporarily unavailable. please try again later."
    }
    
    TRANSACTION_STATES = {
        "PENDING" : 1,
        "SUCCESSFUL": 2,
        "FAILED": 4
    }

    def __init__(self):

        self.subscription_key = settings.MTN_SUBSCRIPTION_KEY
        self.api_user = settings.MTN_API_USER
        self.api_key = settings.MTN_API_KEY
        self.bearer_auth_token_filename = "token.json"
        self.bearer_auth_token = self.load_bearer_auth_token()
        self.basic_auth_token = self.get_basic_auth_token()
        self.environment = "sandbox" if settings.DEBUG else "live"
        self.base_http_headers = {
            "X-Target-Environment" : self.environment,
            "Ocp-Apim-Subscription-Key" : self.subscription_key,
            "Authorization": "Basic %s" %(self.basic_auth_token), # Default authentication set to Basic
        }

    def debit_funds(self, payload):
        transaction_reference = payload.transaction_reference
        payload = self.create_debit_funds_payload(payload)
        
        bearer_auth_token =  self.get_bearer_auth_token()
        http_headers = self.base_http_headers.copy()
        authorization_header_value = "Bearer %s" %(bearer_auth_token["access_token"])
        http_headers = self.add_to_http_headers(http_headers, "Authorization", authorization_header_value)
        http_headers = self.add_to_http_headers(http_headers, "X-Reference-Id", transaction_reference)

        http_response = requests.post("%s/v1_0/requesttopay" %(self.__class__.BASE_URL), headers=http_headers, json=payload)
        if http_response.status_code != 202:
            self.raise_exception(http_response)
            
        return transaction_reference
        
    def get_transaction_state(self, transaction_reference: str):
        bearer_auth_token =  self.get_bearer_auth_token()
        http_headers = self.base_http_headers.copy()
        authorization_header_value = "Bearer %s" %(bearer_auth_token["access_token"])
        http_headers = self.add_to_http_headers(http_headers, "Authorization", authorization_header_value)
        http_response = requests.get("%s/v1_0/requesttopay/%s" %(self.__class__.BASE_URL, transaction_reference), headers=http_headers)
        # The authorization is header is optional for this endpoint though I am send it too
        if http_response.status_code != 200:
           self.raise_exception(http_response)
            
        transaction_state = http_response.json()["status"]
        
        return self.__class__.TRANSACTION_STATES[transaction_state]

    def get_bearer_auth_token(self):
        
        http_headers = self.base_http_headers.copy()
        bearer_auth_token = self.bearer_auth_token
        
        # Authorization used for this endpoint is Basic
        http_headers["Authorization"] = "Basic %s" %(self.basic_auth_token)

        # X-target-Environment header not allowed for this endpoint 
        http_headers = self.delete_from_http_headers(http_headers, "X-Target-Environment")

        if self.is_bearer_auth_token_expired():
            http_response = requests.post("%s/token/" %(self.__class__.BASE_URL), headers=http_headers)
            if http_response.status_code != 200:
                # An error has occured
                self.raise_exception(http_response)            

            bearer_auth_token = http_response.json()
            # Save token to file
            self.dump_bearer_auth_token()
            
        return bearer_auth_token

            
    def is_bearer_auth_token_expired(self) -> bool:
        """ 
        True is returned for two cases:
         1) Token expiration
         2) and when the bearer auth token has not yet been requested from the API

        """
        
        seconds_allowed_before_expiry = 30
        if self.bearer_auth_token:
            seconds_remaining_before_expiry = self.bearer_auth_token["expires_at"] - time.time()
            if  seconds_remaining_before_expiry > seconds_allowed_before_expiry:
                return False 
        return True
        
    def dump_bearer_auth_token(self):
        with open(self.bearer_auth_token_filename, "w") as f:
            json.dump(self.bearer_auth_token, f, indent=4)

    def load_bearer_auth_token(self):
        bearer_auth_token = {}
        if os.path.exists(self.bearer_auth_token_filename):
            with open(self.bearer_auth_token_filename, "r") as f:
                bearer_auth_token = json.load(f)
        return bearer_auth_token
        
    def get_basic_auth_token(self):
        basic_auth_credentials = "%s:%s" %(self.api_user, self.api_key)
        basic_auth_credentials_bytes = basic_auth_credentials.encode("ascii")
        return base64.b64encode(basic_auth_credentials_bytes).decode("ascii")

    
    def delete_from_http_headers(self, http_headers, http_header_key):
        del http_headers[http_header_key]
        return http_headers

    def set_http_header(self, http_header_key, http_header_value):
        self.headers[http_header_key] = http_header_value

    def add_to_http_headers(self, http_headers, http_header_key, http_header_value):
        http_headers[http_header_key] = http_header_value

        return http_headers

    def set_bearer_auth_token(self, bearer_auth_token):
        self.bearer_auth_token["expires_at"] = int(bearer_auth_token["expires_in"]) + time.time()
        self.bearer_auth_token["access_token"] = bearer_auth_token["access_token"]

    def create_debit_funds_payload(self, payload):
        payload = {

            "amount": payload.amount_ugx,
            "currency": "EUR",
            "externalId": payload.transaction_id,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": payload.phone_no
            },
            "payerMessage": "Purchasing electricity token.",
            "payeeNote": "Purchasing electricity token."
        }
        return payload
        

    def raise_exception(self, http_response):
        error_message = "Unknown error"
        http_response_status_code = http_response.status_code
        if len(http_response.text) != 0:
            # In some cases, the server responds with a particular message detailing the cause of the error
            error_message = http_response.json()["message"]

        error_message = self.__class__.ERRORS.get(http_response_status_code, error_message)
        raise MTNMobileMoneyException(http_response_status_code, error_message)
    
        
    
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
            
            "AccountID": str(payload.meter_owner_id),
            "CustomerID": random_customer_id,
            "CustomerName": payload.meter_owner_name,
            "CustomerAddress": payload.meter_owner_address,
            "CustomerPhone": payload.meter_owner_phone_no,
            "CustomerEmail": payload.meter_owner_email,
            "PriceCategories": payload.meter_price_category,
            "MeterID": payload.meter_no,
            "MeterType": 0
        }

        payload.update(self.payload)

        response = self.request("NewCustomer", payload)

        response_text = response.text.strip('"')
        if response_text == "true":
            return True

        """Should I just raise exceptions instead of returning booleans????"""
        return False
    
    
        

    def register_price_category(self, payload) -> bool:

        payload = {
    
            "PRICE_ID": payload.pk,
            "Categories": payload.label,
            "PRICE": payload.price,
            "VAT_RATE": 0.0,
            "PRICE_UNIT": "UGX",
            "REMARK": "Registering Price Category"
        }
        # Set username and password 
        payload.update(self.payload)
        
        response = self.request("NewPrice", payload)
            
        response_text = response.text.strip('"')
        if response_text == "true":
            return True
        # Realised that the API is not consistent with the error messages(In some cases, they contain no debugging info - reason for the error)
        # it returns
        return False
            
    def get_token(self, payload) -> dict:
        payload = {

            "MeterID": payload.meter_no,
            "is_vend_by_unit": "false",
            "Amount": payload.amount_ugx
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
                 "num_of_units": response[0]["Total_units"],
                 "unit": response[0]["Unit"],
               }
    
    def raise_exception(self, code: int, message: str):
        raise StronPowerException(code, message)


    def request(self, endpoint: str, payload):
        response = requests.post("%s/%s" %(StronPower.BASE_URL, endpoint), json=payload)
        if response.status_code != 200:
            self.raise_exception(response.status_code, response.text)

        return response


class NotificationException(Exception):

    def __init__(self, message):
        self.message = message
        super(NotificationException, self).__init__(message)

    def __str__(self):
        return message
    
    
class Notification(abc.ABC):

    @abc.abstractmethod
    def send(self, source, destination, message):
        raise NotImplementedError


class NotificationClient(abc.ABC):

    @abc.abstractmethod
    def send(self, source, destination, message):
        raise NotImplementedError


class TwilioSMSClient(NotificationClient):

    def __init__(self, account_sid, authentication_token):
        self.account_sid = account_sid
        self.authentication_token = authentication_token
        self.client = Client(account_sid, authentication_token)

    def send(self, source, destination, message):
        message = self.client.messages.create(body=message, from_=source, to=destination)
        return message
    
    
class NotificationImpl(Notification):
    
    def __init__(self, client):
        self.client = client
        
    def send(self, source, destination, message):
        self.client.send(source, destination, message)
