# Generated by Django 4.1 on 2022-09-06 08:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('meter', '0001_initial'),
        ('meter_manufacturer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meter',
            name='manager',
            field=models.ForeignKey(limit_choices_to={'account_type': 4}, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='meter',
            name='manufacturer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='meter_manufacturer.metermanufacturer'),
        ),
    ]
