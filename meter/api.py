from uuid import uuid4
import requests
import base64
import time



""" This is the abstraction of the stron api and MTN MoMo api """

class MTNMoMoException(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code # Status code returned by MTNMoMo api
        self.message = message  # A description message attached to elucidate the status code
        super().__init__(self.message) # Call Exception class Constructor

    def __str__(self):
        return "%d - %s" %(self.status_code, self.message)
    

class StronException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message

    
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

    def __init__(self, subscription_key, api_user, api_key, target_env="sandbox"):
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

    def request_to_pay(self, payload):
        
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
        if self.__is_acess_token_expired():
            self.request_access_token() # This method modifies the headers attribute, call it before copying the headers
            
        headers = self.headers.copy() # Avoid altering the base headers template because not all endpoints will need the headers
        # added by some endpoints
        reference_id = str(uuid4())
        headers["X-Reference-Id"] = reference_id  # This is the uuuid that will be used to identify the transaction

        response = requests.post("%s/v1_0/requesttopay" %(MTNMoMo.BASE_URL), headers=headers, json=payload)
        if response.status_code != 202:
            self.raise_exception(response.status_code)

        return reference_id # Use the reference_id for querying about the status of the transaction
        
    def request_transaction_status(self, reference_id):
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
           self. raise_exception(response.status_code)
            
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
            self.raise_exception(response.status_code)            

        data = response.json()
        self.access_token["expires_at"] = int(data["expires_in"]) + time.time()
        self.access_token["access_token"] = data["access_token"]
        # Update the headers to reflect the new access token, remember, authorization is Bearer
        self.headers["Authorization"] = "Bearer %s" %(data["access_token"])

        return data["access_token"] # The invoker may need to use the token

    def raise_exception(self, code):
        unknown_error_msg = "Unknown error!"
        raise MTNMoMoException(code, MTNMoMo.ERRORS.get(code, unknown_error_msg))

            
    def __is_acess_token_expired(self):
        if self.access_token:
            if time.time() >= self.access_token["expires_at"]:
                return True
        # False is returned for two cases: Token expiration and When the token has not yet been requested
        return False

    def __create_basic_auth_token(self):
        s = "%s:%s" %(self.api_user, self.api_key)
        bytes_str = s.encode("ascii")
        return base64.b64encode(bytes_str).decode("ascii") 


class Stron:

    BASE_URL = "http://www.server-api.stronpower/api"

    def __init__(self, username, pwd):
        self.username = username
        self.pwd = pwd

    def register_new_customer(self):
        pass

    def set_new_price_per_unit(self):
        pass

    def buy_token(self):
        pass
