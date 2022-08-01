import uuid


class DTO:

    def __init__(self):
        self.API = None

    
class MeterCustomer(DTO):

    def __init__(self, customer):
        self.object = customer
        self.unit_price_label = "API-STANDARD"

    def get_full_name(self):
        return "%s %s" %(self.object.first_name, self.object.last_name)
    
    def get_email(self):
        return self.object.email

    def get_address(self):
        return self.object.address

    def get_phone_no(self):
        return self.object.phone_no

    def get_id(self):
        return str(uuid.uuid4())

    def set_meter(self, meter):
        self.meter = meter

            
class TokenSpec(DTO):
    
    def __init__(self):
        self.meter = None
        self.buyer = None
        self.num_of_units = 0
        self.amount = 0
        
    def get_meter_no(self):
        return self.meter.meter_no


class Token(TokenSpec):

    def __init__(self):
        super(TokenSpec, self).__init__()
        self.number = ""
        self.unit = ""
