import requests
import abc
import time
import base64
import os

from django.conf import settings

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


class MobileMoneyAPIFactoryImpl(MobileMoneyFactory):

    @classmethod
    def create_api(self, api_name: str):
        if api_name.lower() == "airtel":
            return AirtelMoney()
        elif api_name.lower() == "mtn":
            return MTNMobileMoney()
        else:
            return None
        

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
    
        
