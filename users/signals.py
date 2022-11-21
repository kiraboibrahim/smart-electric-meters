from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from users.account_types import MANAGER
from users.models import UnitPrice

User = get_user_model()


@receiver(post_save, sender=User)
def create_default_manager_unit_price(sender, instance, created, **kwargs):
    if instance.account_type == MANAGER and created:
        UnitPrice.objects.create(manager=instance)
