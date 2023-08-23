import requests
import logging

from django.conf import settings as django_settings

from ..base import NotificationBackend
from ..exceptions import FailedSMSDeliveryException

from . import settings

logger = logging.getLogger(__name__)


class TrueAfricanSMSBackend(NotificationBackend):
    USERNAME = settings.USERNAME
    PASSWORD = settings.PASSWORD
    SUCCESSFUL_SMS_DELIVERY_CODE = 200
    SMS_SEND_URL = "https://mysms.trueafrican.com/v1/api/esme/send/"

    def send(self, to: list[str], subject: str, message: str):
        payload = {
            "msisdn": list(map(lambda p: p.lstrip("+"), to)),
            "message": f"{message}",
            "username": self.USERNAME,
            "password": self.PASSWORD
        }
        try:
            proxies = django_settings.PROXIES if django_settings.DEBUG is True else {}
            response = requests.post(self.SMS_SEND_URL, json=payload, proxies=proxies).json()
            if response["code"] != self.SUCCESSFUL_SMS_DELIVERY_CODE:
                logger.error(f"Failed to send sms: {response['error']}")
                raise FailedSMSDeliveryException(f"{response['error']}")
        except Exception as exc:
            logger.exception(str(exc))
            raise FailedSMSDeliveryException(str(exc))
