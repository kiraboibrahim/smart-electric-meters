class MeterVendorAPINotFoundException(Exception):
    pass


class MissingPayloadAttributeException(Exception):
    pass


class MeterVendorAPIException(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return "%d: %s" % (self.status_code, self.message)


class MeterRegistrationException(MeterVendorAPIException):
    def __init__(self):
        self.status_code = 500
        self.message = "Meter registration failure. Contact the meters vendor support"


class EmptyTokenResponseException(MeterVendorAPIException):

    def __init__(self):
        self.status_code = 500
        self.message = "No token received. Contact the meters vendor support"
