# Generated by Django 3.2.19 on 2023-08-03 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='external_id',
            field=models.CharField(max_length=255, null=True, unique=True),
        ),
    ]