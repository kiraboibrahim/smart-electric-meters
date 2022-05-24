from twilio.rest import Client # Messaging client
import requests
import base64
import time
import json
import abc
import os


class MTNMoMoException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code # Status code returned by MTNMoMo api
        self.message = message  # A description message attached to elucidate the status code
        super().__init__(self.message) # Call Exception class Constructor

    def __str__(self):
        return "%s - %s" %(str(self.status_code), self.message)

    
class AirtelMoneyException(MTNMoMoException):
    def __init__(self, status_code: int, message: str):
        super.__init__(status_code, message)
        
    

class StronException(Exception):
    def __init__(self, status_code: int, message: str = ""):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self):
        return "Response Status Code: %d" %(self.status)

        

meter_api_classes = {}

def register(cls):
    """
    This function registers all meter api classes so that the factory method can easily instantiate the meter api classes
    """
    meter_api_classes[cls.__name__.lower()] = cls
    return cls


class MeterApiInterface(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_token(self, payload: dict) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    def register_meter_customer(self, payload: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def set_price_per_unit(self, payload: dict):
        raise NotImplementedError
    

class MeterApiFactoryInterface(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_api(self, type: str) -> MeterApiInterface:
        raise NotImplementedError


class MeterApiFactory(MeterApiFactoryInterface):
    
    @classmethod
    def create_api(cls, company_name: str, *args, **kwargs) -> MeterApiInterface:
        class_ = meter_api_classes.get(company_name.lower(), None)
        if class_ is not None:
            return class_(*args, **kwargs)
        raise Exception("Meter API for %s has not been added yet." %(company_name))


class MobileMoneyApiInterface(metaclass=abc.ABCMeta):
    
    @abc.abstractmethod
    def request_to_pay(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def request_transaction_status(self, *args, **kwargs):
        raise NotImplementedError

    
class MobileMoneyApiFactoryInterface(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_api(self, service_provider: str) -> MeterApiInterface:
        raise NotImplementedError
    

class MobileMoneyApiFactory(MeterApiFactoryInterface):

    @classmethod
    def create_api(self, service_provider: str, *args, **kwargs) -> MobileMoneyApiInterface:
        if service_provider.lower() == "airtel":
            return AirtelMoney(*args, **kwargs)
        elif service_provider.lower() == "mtn":
            return MTNMoMo(*args, **kwargs)
        else:
            return None

        
class AirtelMoney(MobileMoneyApiInterface):

    def __init__(self, *args, **kwargs):
        pass

    def request_to_pay(self, *args, **kwargs):
        raise NotImplementedError

    def request_transaction_status(self, *args, **kwargs):
        raise NotImplementedError
    
    
class MTNMoMo(MobileMoneyApiInterface):
    # Only using the collection service
    BASE_URL = "https://sandbox.momodeveloper.mtn.com/collection"
    # These are descriptions of the error codes returned as shown in the mtnmomo documentation: https://momodeveloper.mtn.com/api-documentation/common-error/
    # The error codes below are all in the generic context except for the 500 error code which is interpreted in the requesttopay context (I am only using requesttopay, no need to bother with generic context though it may apply in certain scenarios)
    
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

    def __init__(self, subscription_key: str, api_user: str, api_key: str, env: str ="sandbox"):
        self.subscription_key = subscription_key
        self.api_user = api_user
        self.api_key = api_key
        self.bearer_auth_token_filename = "token.json"
        self.bearer_auth_token = {}
        self.basic_auth_token = self.create_basic_auth_token()
        self.headers = {
            "X-Target-Environment" : env,
            "Ocp-Apim-Subscription-Key" : subscription_key,
            "Authorization": "Basic %s" %(self.basic_auth_token), # Default authentication set to Basic
        }

    def request_to_pay(self, reference_id: str, payload: dict) -> str:
        
        """
        Request payments from the clients mobile wallet, thet are prompted for the mobile money pin
        """
        if self.is_bearer_auth_token_expired():
            self.request_bearer_auth_token() # This method modifies the headers attribute, call it before copying the headers
            
        headers = self.headers.copy() # Make a copy of the base headers and just extend from
        headers["X-Reference-Id"] = reference_id
        
        response = requests.post("%s/v1_0/requesttopay" %(MTNMoMo.BASE_URL), headers=headers, json=payload)
        if response.status_code != 202:
            self.raise_exception(response)

        return reference_id # Use the reference_id for querying about the status of the transaction
        
    def request_transaction_status(self, reference_id: str) -> int:
        """
        Status of a transaction can be:

        State        Mask
        =================
        PENDING    |  1
        SUCCESSFUL |  2
        FAILED     |  4

        """
        response = requests.get("%s/v1_0/requesttopay/%s" %(MTNMoMo.BASE_URL, reference_id), headers=self.headers)
        # The authorization is header is optional for this endpoint though I am send it too
        if response.status_code != 200:
           self.raise_exception(response)
            
        transaction_status = response.json()["status"]
        
        return MTNMoMo.TRANSACTION_STATES[transaction_status]

    def request_bearer_auth_token(self):
        """
        Request for token that can be used for Bearer authorization, Remeber the token expires, 
        so you have to request another one
        
        """
        headers = self.headers.copy()
        # Authorization used for this endpoint is Basic
        headers["Authorization"] = "Basic %s" %(self.basic_auth_token)

        # X-target-Environment header not allowed for this endpoint 
        del headers["X-Target-Environment"]

        bearer_auth_token = self.load_bearer_auth_token()
        if not bearer_auth_token:
            response = requests.post("%s/token/" %(MTNMoMo.BASE_URL), headers=headers)
            if response.status_code != 200:
                # An error has occured
                self.raise_exception(response)            

            bearer_auth_token = response.json()
            self.bearer_auth_token["expires_at"] = int(bearer_auth_token["expires_in"]) + time.time()
            self.bearer_auth_token["access_token"] = bearer_auth_token["access_token"]
            self.dump_bearer_auth_token() # Save token to file
                
        # Update the headers to reflect the new access token, remember, authorization is Bearer
        self.headers["Authorization"] = "Bearer %s" %(bearer_auth_token["access_token"])

        return bearer_auth_token["access_token"] # The invoker may need to use the token

    def raise_exception(self, response):
        error_msg = "Unknown error!"
        code = response.status_code
        if len(response.text) != 0:
            # In some cases, the server responds with helpful debugging info rather than the generic ones as defined in ERRORS variable
            err_json = response.json()
            raise MTNMoMoException(code, err_json["message"])
        else:
            raise MTNMoMoException(code, MTNMoMo.ERRORS.get(code, error_msg))
            
    def is_bearer_auth_token_expired(self) -> bool:
        # True is returned for two cases: Token expiration and When the token has not yet been requested
        if self.bearer_auth_token:
            # I am using 30 as offset below which the token is logically rendered expired because of
            # the network latency, the token may become expired during the course of the request,
            # 30 seconds may not be enough
            if self.bearer_auth_token["expires_at"] - time.time() > 30:
                return False
            else:
                return True
        else:
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
        
    def create_basic_auth_token(self):
        s = "%s:%s" %(self.api_user, self.api_key)
        bytes_str = s.encode("ascii")
        return base64.b64encode(bytes_str).decode("ascii") 

    
@register
class StronPower(MeterApiInterface):

    BASE_URL = "http://www.server-api.stronpower.com/api"
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        
        # Every payload should have username and password fields
        self.payload = {
            "UserName": self.username,
            "PassWord": self.password,
        }

    def register_meter_customer(self, payload: dict) -> bool:
        payload.update(self.payload)

        response = self.request("NewCustomer", payload)

        response_text = response.text.strip('"')
        if response_text == "true":
            return True

        return False
        

    def set_price_per_unit(self, payload: dict) -> bool:
        # Set username and password 
        payload.update(self.payload)
        
        response = self.request("NewPrice", payload)
            
        response_text = response.text.strip('"')
        if response_text == "true":
            return True
        # Realised that the API is not consistent with the error messages(In some cases, they contain no debugging info - reason for the error)
        # it returns
        return False
            
    def get_token(self, payload : dict, vending_money: bool = True) -> dict:
        # Upadate with the username and password
        payload.update(self.payload)
        # By default, vending will be done by money ie the customer enters the amount of money and
        # remeber money should never be less than the price_per_unit
        if not vending_money:
            payload["is_vend_by_unit"] = "true" # Vending by units
            
        response = self.request("VendingMeter", payload)
        response = response.json()
        if response == []:
            # It is an empty response, some error have been triggered but the api doesnot give helpful info
            return {}

        return {
                 "token": response[0]["Token"],
                 "created_at": response[0]["Gen_time"],
                 "num_of_units": response[0]["Total_units"],
                 "unit": response[0]["Unit"],
               }
    
    def raise_exception(self, code: int, message: str):
        raise StronException(code, message)


    def request(self, endpoint: str, payload: dict):
        response = requests.post("%s/%s" %(StronPower.BASE_URL, endpoint), json=payload)
        if response.status_code != 200:
            self.raise_exception(response.status_code, response.text)

        return response



class SMS:

    """
    Send messages with twilio sms api
    """
    def __init__(self, account_sid: str, auth_token: str, from_: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_ = from_
        self.client = Client(account_sid, auth_token)
    
    def send(self, to: str = "", body: str = "") -> int:
        message = self.client.messages.create(body=body, from_=self.from_, to=to)
        return message.sid

