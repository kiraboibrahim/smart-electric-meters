from django.db import models
from django.conf import settings

from shared.decorators import ignore_table_does_not_exist_exception


class ChargesCategoryManager(models.Manager):

    @ignore_table_does_not_exist_exception
    def create_default_charges_category(self):
        lookup, defaults = self._get_default_charges_category_config()
        defaults["is_default"] = True
        default_category, is_created = self.get_or_create(**lookup, defaults=defaults)
        return default_category

    @ignore_table_does_not_exist_exception
    def get_default_charges_category(self):
        lookup, _ = self._get_default_charges_category_config()
        return self.get(**lookup)

    @staticmethod
    def _get_default_charges_category_config():
        lookup = {
            settings.DEFAULTS["CHARGES_CATEGORY"]["lookup_field"]: settings.DEFAULTS["CHARGES_CATEGORY"]["lookup_value"]
        }
        defaults = settings.DEFAULTS["CHARGES_CATEGORY"]["defaults"]
        return lookup, defaults
