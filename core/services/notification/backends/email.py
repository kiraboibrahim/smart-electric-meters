from django.conf import settings
from django.core.mail import send_mail

from .base import NotificationBackend


class EmailNotificationBackend(NotificationBackend):

    def send(self, recipients, subject, message):
        send_mail(subject, message, settings.FROM_EMAIL, recipients, html_message=message)
