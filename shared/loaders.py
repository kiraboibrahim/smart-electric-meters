import pathlib

from django.conf import settings
from django.template.loaders.filesystem import Loader as FileSystemLoader


class ProductionDevelopmentLoader(FileSystemLoader):

    def get_template_sources(self, template_name):
        if settings.DEBUG is True:
            template_name = str(pathlib.PurePath(template_name).with_suffix("development"))
        return super().get_template_sources(template_name)
