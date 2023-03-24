from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UnitPrice

User = get_user_model()


@receiver(post_save, sender=User)
def create_manager_unit_price(sender, instance, created, **kwargs):
    if(instance.is_manager() or instance.is_default_manager()) and created:
        UnitPrice.objects.create(manager=instance)
