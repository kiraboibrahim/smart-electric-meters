# Generated by Django 3.2.19 on 2023-08-09 13:28

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import migrations, models
import django.db.models.deletion

User = get_user_model()
default_manager = User.objects.get_default_manager()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('meter_vendors', '0003_alter_metervendor_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Meter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meter_number', models.CharField(max_length=11, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_registered_with_vendor', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('manager', models.ForeignKey(default=default_manager.id, limit_choices_to=models.Q(('account_type', 4), ('account_type', 8), _connector='OR'), on_delete=django.db.models.deletion.PROTECT, related_name='meters', to=settings.AUTH_USER_MODEL)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='meters', to='meter_vendors.metervendor')),
            ],
            options={
                'ordering': ['manager'],
            },
        ),
        migrations.CreateModel(
            name='MeterMonthlyFeePaymentLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_paid_at', models.DateTimeField()),
                ('meter', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='meters.meter')),
            ],
        ),
    ]
