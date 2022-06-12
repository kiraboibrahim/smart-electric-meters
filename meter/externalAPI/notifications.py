import abc

from twilio.rest import Client


class NotificationException(Exception):

    def __init__(self, message):
        self.message = message
        super(NotificationException, self).__init__(message)

    def __str__(self):
        return message
    
    
class Notification(abc.ABC):

    @abc.abstractmethod
    def send(self, source, destination, message):
        raise NotImplementedError


class NotificationClient(abc.ABC):

    @abc.abstractmethod
    def send(self, source, destination, message):
        raise NotImplementedError


class TwilioSMSClient(NotificationClient):

    def __init__(self, account_sid, authentication_token):
        self.account_sid = account_sid
        self.authentication_token = authentication_token
        self.client = Client(account_sid, authentication_token)

    def send(self, source, destination, message):
        message = self.client.messages.create(body=message, from_=source, to=destination)
        return message
    
    
class NotificationImpl(Notification):
    
    def __init__(self, client):
        self.client = client
        
    def send(self, source, destination, message):
        self.client.send(source, destination, message)
