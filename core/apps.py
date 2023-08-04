from django.apps import AppConfig
from django.urls import register_converter

from .converters import HashIdConverter


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        register_converter(HashIdConverter, "hashid")
