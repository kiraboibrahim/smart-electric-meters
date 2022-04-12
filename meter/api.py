from uuid import uuid4
from twilio.rest import Client # Messaging client
import requests
import base64
import time
import json
import abc

request_to_pay_payload = {
    "amount": "",
    "currency": "UGX",
    "externalId": "",
    "payer": {
        "partyIdType": "MSISDN",
        "partyId": ""
    },
    "payerMessage": "",
    "payeeNote": ""
}

register_new_customer_payload = {
    "CompanyName": "",
    "UserName": "",
    "PassWord": "",
    "AccountID": "",
    "CustomerID": "",
    "CustomerName": "",
    "CustomerAddress": "",
    "CustomerPhone": "",
    "CustomerEmail": "",
    "PriceCategories": "",
    "MeterID": "",
    "MeterType": 0
}

buy_token_payload = {
    "CompanyName": "",
    "UserName": "",
    "PassWord": "",
    "MeterID": "",
    "is_vend_by_unit": "false",
    "Amount": 0
}

set_new_price_per_unit_payload = {
    "CompanyName": "",
    "UserName": "",
    "PassWord": "",
    "PRICE_ID": "",
    "Categories": "",
    "PRICE": 0,
    "VAT_RATE": 0,
    "PRICE_UNIT": "UGX",
    "REMARK": ""
}
        

class ManufacturerAPIInterface(metaclass=abc.ABCMeta):
    
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, "buy_token") and callable(subclass.buy_token) or NotImplementedError)

    @abc.abstractmethod
    def buy_token(self, payload: dict) -> dict:
        raise NotImplementedError

    

""" This is the abstraction of the stron api and MTN MoMo api """

class MTNMoMoException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code # Status code returned by MTNMoMo api
        self.message = message  # A description message attached to elucidate the status code
        super().__init__(self.message) # Call Exception class Constructor

    def __str__(self):
        return "%s - %s" %(str(self.status_code), self.message)
    

class StronException(Exception):
    def __init__(self, status_code: int, message: str = ""):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self):
        return "Response Status Code: %d" %(self.status)

    
class MTNMoMo:
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

    def __init__(self, subscription_key: str, api_user: str, api_key: str, target_env: str ="sandbox"):
        self.subscription_key = subscription_key
        self.api_user = api_user
        self.api_key = api_key
        self.access_token = {}
        self.basic_auth_token = self.__create_basic_auth_token()
        self.headers = {
            "X-Target-Environment" : target_env,
            "Ocp-Apim-Subscription-Key" : subscription_key,
            "Authorization": "Basic %s" %(self.basic_auth_token), # Default authentication set to Basic
        }

    def request_to_pay(self, payload: dict) -> str:
        
        """
        Request payments from the clients mobile wallet, thet are prompted for the mobile money pin
        {
          "amount": "string",
          "currency": "string",
          "externalId": "string",
          "payer": {
            "partyIdType": "MSISDN",
            "partyId": "string"
          },
          "payerMessage": "string",
          "payeeNote": "string"
        }
        
        """
        if self.__is_access_token_expired():
            self.request_access_token() # This method modifies the headers attribute, call it before copying the headers
            
        headers = self.headers.copy() # Avoid altering the base headers template because not all endpoints will need the headers
        # added by some endpoints
        reference_id = str(uuid4())
        headers["X-Reference-Id"] = reference_id  # This is the uuuid that will be used to identify the transaction

        response = requests.post("%s/v1_0/requesttopay" %(MTNMoMo.BASE_URL), headers=headers, json=payload)
        if response.status_code != 202:
            self.raise_exception(response)

        return reference_id # Use the reference_id for querying about the status of the transaction
        
    def request_transaction_status(self, reference_id: str) -> int:
        """
        Status of a transaction can be:
        s/n   state        mask
        1.    PENDING      1
        2.    SUCCESSFUL   2
        3.    FAILED       4
        """
        response = requests.get("%s/v1_0/requesttopay/%s" %(MTNMoMo.BASE_URL, reference_id), headers=self.headers)
        # The authorization is header is optional for this endpoint though I am send it too
        if response.status_code != 200:
           self.raise_exception(response)
            
        transaction_status = response.json()["status"]
        
        return MTNMoMo.TRANSACTION_STATES[transaction_status]

    def request_access_token(self):
        """
        Request for token that can be used for Bearer authorization, Remeber the token expires, so you have to request another one
        """
        headers = self.headers.copy()
        # Authorization used for this endpoint is Basic
        headers["Authorization"] = "Basic %s" %(self.basic_auth_token)
        # X-target-Environment header not required for this endpoint 
        del headers["X-Target-Environment"]
        
        response = requests.post("%s/token/" %(MTNMoMo.BASE_URL), headers=headers)
        if response.status_code != 200:
            # An error has occured
            self.raise_exception(response)            

        data = response.json()
        self.access_token["expires_at"] = int(data["expires_in"]) + time.time()
        self.access_token["access_token"] = data["access_token"]
        # Update the headers to reflect the new access token, remember, authorization is Bearer
        self.headers["Authorization"] = "Bearer %s" %(data["access_token"])

        return data["access_token"] # The invoker may need to use the token

    def raise_exception(self, response):
        unknown_error_msg = "Unknown error!"
        code = response.status_code
        if len(response.text) != 0:
            # Sometimes the server responds with helpful debugging info rather than the generic ones as defined in ERRORS variable
            err_json = response.json()
            raise MTNMoMoException(code, err_json["message"])
        else:
            raise MTNMoMoException(code, MTNMoMo.ERRORS.get(code, unknown_error_msg))
            
    def __is_access_token_expired(self) -> bool:
        # True is returned for two cases: Token expiration and When the token has not yet been requested
        if self.access_token:
            # I am using 10 as offset below which the token is logically rendered expired because of
            # the network latency, the token may become expired during the course of the request,
            # 30 seconds may not be enough
            if self.access_token["expires_at"] - time.time() > 30:
                return False
            else:
                return True
        else:
            return True
        
        
    def __create_basic_auth_token(self):
        s = "%s:%s" %(self.api_user, self.api_key)
        bytes_str = s.encode("ascii")
        return base64.b64encode(bytes_str).decode("ascii") 


class StronPower(ManufacturerAPIInterface):

    BASE_URL = "http://www.server-api.stronpower.com/api"
    
    def __init__(self, username: str, pwd: str):
        self.username = username
        self.pwd = pwd
        # Every payload should have username and password fields
        self.payload = {
            "UserName": self.username,
            "PassWord": self.pwd,
        }

    def register_new_customer(self, payload: str) -> bool:
        payload.update(self.payload)

        response = self.__request("NewCustomer", payload)

        response_text = response.text.strip('"')
        if response_text == "true":
            return True

        return False
        

    def set_new_price_per_unit(self, payload: str) -> bool:
        
        """
        The post body is as follows, On success, It returns a 200 status code, price_id must be unique
        {
P         "CompanyName": " your company name ",
          "UserName": "xxxx",
          "PassWord": "xxxxxxxx",
          "PRICE_ID": "0003",
          "Categories": "HomeChargePrice",
          "PRICE": 705.1282,
          "VAT_RATE": 7.5,
          "PRICE_UNIT": "NGN",
          "REMARK": "Test"
        }
        """
        # Set username and password 
        payload.update(self.payload)
        
        response = self.__request("NewPrice", payload)
            
        response_text = response.text.strip('"')
        if response_text == "true":
            return True
        # Realised that the API is not consistent with the error messages(In some cases, they contain no debugging info - reason for the error)
        # it returns
        return False
            
    def buy_token(self, payload : dict, vending_money: bool = True):
        """
        Payload fields
        {
          "CompanyName": " your company name ",
          "UserName": " your user name ",
          "PassWord": " your password ",
          "MeterID": "string"
          "is_vend_by_unit": "true: vending unit . false: vending money ",
          "Amount": 0
        }
        """
        # Upadate with the username and password
        payload.update(self.payload)
        # By default, vending will be done by money ie the customer enters the amount of money and
        # remeber money should never be less than the price_per_unit
        if not vending_money:
            payload["is_vend_by_unit"] = "true" # Vending by units
            
        response = self.__request("VendingMeter", payload)
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


    def __request(self, endpoint: str, payload: dict):
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

