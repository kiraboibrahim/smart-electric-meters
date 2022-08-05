from django.conf import settings

from meter.externalAPI.notifications import NotificationImpl, TwilioSMSClient

def send_sms(source, destination, message):
    sms_client = TwilioSMSClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    notification = NotificationImpl(sms_client)
    notification.send(source, destination, message)
