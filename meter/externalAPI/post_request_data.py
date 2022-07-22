import uuid


class PostRequestData:
    
    def set_API(self, API):
        self.API = API

    
class MeterCustomer(PostRequestData):

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


class TokenSpec(PostRequestData):
    
    def set_num_of_units(self, value):
        self.num_of_units = value

    def set_meter(self, meter):
        self.meter = meter

    def get_meter_no(self):
        return self.meter.meter_no

    def get_token(self):
        self.API.get_token(self)
        
    

class UnitPrice(PostRequestData):

    def __init__(self, unit_price):
        self.unit_price = unit_price

    def register(self):
        self.API.register_unit_price(self)
        
