################################################################################################################
# These are payload used by various endpoints. To prevent altering the client code, The only known fact is the #
# external APIs will use data from a certain entity which is already known before hand, and thus providing the #
# entity and letting external APIs decide which attributes it might require. In this way the client code only  #
# required entity.                                                                                             #
################################################################################################################


class NewMeterCustomer():
    def __init__(self, meter, meter_owner):
        self.meter = meter
        self.meter_owner = meter_owner
        
        self.meter_no = meter.meter_no
        self.meter_price_category = meter_owner.priceperunit.label
        
        # Manager Information
        self.meter_owner_id = meter_owner.id
        self.meter_owner_name = "%s %s" %(meter_owner.first_name, meter_owner.last_name)
        self.meter_owner_address = meter_owner.address
        self.meter_owner_phone_no = meter_owner.phone_no
        self.meter_owner_email = meter_owner.email


class GetToken():
    def __init__(self, meter, amount_ugx):
        self.meter = meter
        self.meter_no = meter.meter_no
        self.amount_ugx = amount_ugx



class NewPriceCategory():
    def __init__(self, price_category):
        self.price_category = price_category
        self.id = str(price_category.id)
        self.label = price_category.label
        self.price_ugx = price_category.price_per_unit
        


class DebitFunds():
    def __init__(self, phone_no, amount_ugx, transaction_id, transaction_reference):
        self.phone_no = phone_no
        self.amount_ugx = str(amount_ugx)
        self.transaction_id = transaction_id
        self.transaction_reference= transaction_reference
