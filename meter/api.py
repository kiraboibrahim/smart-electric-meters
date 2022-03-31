import requests
import json
import base64

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
    BASE_URL = "https://sandbox.momodeveloper.mtn.com/collection/v1_0"
    # These are descriptions of the error codes returned as shown in the mtnmomo documentation: https://momodeveloper.mtn.com/api-documentation/common-error/
    # The error codes below are all in the generic context except for the 500 error code which is interpreted in the requesttopay context (I am only using requesttopay, no need to bother with generic context though it may apply in certain scenarios)
    
    ERRORS   = {
        409 : "Duplicated Reference Id. Cannot create new resource.",
        404 : "Reference Id not found. Requestedd resource does not exist.",
        400 : "Bad request. Request does not follow the specification.",
        401 : "Authentication failed. Credentials not valid.",
        403 : "Authorization failed. IP address not allowed to transact.",
        500 : "Payer not found. Account holder not registered. or Payee cannot recieve funds due to... ie transfer limit exceeded or Internal Server Error.",
        503 : "Service temporarily unavailable. please try again later."
    }

    TRANSACTION_PENDING = 1
    TRANSACTION_SUCCESSFUL = 2
    TRANSACTION_FAILED = 4

    def __init__(self, subscription_key, api_user, api_key):
        self.subscription_key = subscription_key
        self.api_user = api_user
        self.api_key = api_key
        self.token = ""

    def request_to_pay(self, amount, payer_phone_no, payer_message, payee_message, external_id, currency="UGX"):
        """
        Request payments from the clients mobile wallet, thet are prompted for the mobile money pin
        """
        pass

    def request_transaction_status(self, reference_id):
        """
        Status of a transaction can be:
        s/n   state        mask
        1.    PENDING      1
        2.    SUCCESSFUL   2
        3.    FAILED       4
        """
        response = requests.get("%s/requesttopay/%s" %(MTNMoMo.BASE_URL, reference_id))
        if response.status_code != 200:
            raise MTNMoMoException(response.status_code, MTNMoMo.ERRORS.get(response.status_code, "Unknown Error"))

    def request_access_token(self):
        """
        Request for token that can be used for Bearer authorization, Remeber the token expires, so you have to request another one
        """
        pass

    def __create_basic_auth_token(self):
        return base64.encode("%s:%s" %(self.api_user, self.api_key))



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
