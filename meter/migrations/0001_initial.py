# Generated by Django 2.2.24 on 2022-04-16 10:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name="Manufacturer's Name")),
            ],
        ),
        migrations.CreateModel(
            name='Meter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meter_no', models.CharField(max_length=11, unique=True, verbose_name='Meter Number')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('manufacturer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='meter.Manufacturer')),
            ],
        ),
        migrations.CreateModel(
            name='MeterType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percentage_charge', models.PositiveIntegerField()),
                ('fixed_charge', models.PositiveIntegerField()),
                ('label', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='TokenHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True, verbose_name="Purchaser's Name")),
                ('token_no', models.PositiveIntegerField(unique=True)),
                ('phone_no', models.CharField(max_length=10)),
                ('amount_paid', models.CharField(max_length=255)),
                ('num_token_units', models.CharField(max_length=255)),
                ('purchased_at', models.DateTimeField(auto_now_add=True)),
                ('meter', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='meter.Meter')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='meter',
            name='meter_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='meter.MeterType'),
        ),
    ]
