# Generated by Django 3.2.19 on 2023-07-22 09:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import users.managers


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('meters', '0009_alter_meter_manager'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meter',
            name='manager',
            field=models.ForeignKey(blank=True, default=users.managers.UserManager.get_default_manager, limit_choices_to=models.Q(('account_type', 4), ('account_type', 8), _connector='OR'), null=True, on_delete=django.db.models.deletion.PROTECT, related_name='meters', to=settings.AUTH_USER_MODEL),
        ),
    ]
