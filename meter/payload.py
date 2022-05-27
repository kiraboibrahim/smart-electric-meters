################################################################################################################
# These are payload used by various endpoints. To prevent altering the client code, The only known fact is the #
# external APIs will use data from a certain entity which is already known before hand, and thus providing the #
# entity and letting external APIs decide which attributes it might require. In this way the client code only  #
# required entity.                                                                                             #
################################################################################################################


class Payload:
    pass


class NewCustomer(Payload):
    def __init__(self, meter):
        self.meter = meter
        
        # Meter Information
        self.meter_no = meter.meter_no
        self.price_category = meter.manger.priceperunit_set.first().label
        
        # Manager Information
        self.pk = meter.manager.id # Our primary key for manager
        self.name = "%s %s" %(meter.manager.first_name, meter.manager.last_name)
        self.address = meter.manager.address
        self.phone_no = meter.manager.phone_no
        self.email = meter.manager.email


class VendingMeter(Payload):
    def __init__(self, meter, amount):
        self.meter = meter
        self.meter_no = meter.meter_no
        self.amount = amount



class NewPrice(Payload):
    def __init__(self, price_category):
        self.price_category = price_category
        self.name = price_category.label
        self.price = price_category.price_per_unit
        self.pk = str(price_category.id)


class RequestToPay(Payload):
    def __init__(self, phone_no, amount, external_id, ref):
        self.phone_no = phone_no
        self.amount = amount
        self.external_id = external_id
        self.ref=ref
