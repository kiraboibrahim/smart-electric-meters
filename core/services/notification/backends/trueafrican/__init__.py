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
            "msisdn": to,
            "message": f"{message}",
            "username": self.USERNAME,
            "password": self.PASSWORD
        }
        try:
            response = requests.post(self.SMS_SEND_URL, json=payload, proxies=django_settings.PROXIES).json()
            if response["code"] != self.SUCCESSFUL_SMS_DELIVERY_CODE:
                logger.error(response["message"])
                raise FailedSMSDeliveryException(response["message"])
        except Exception as e:
            logger.exception(str(e))
            raise FailedSMSDeliveryException
