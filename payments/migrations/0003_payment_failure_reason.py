# Generated by Django 3.2.19 on 2023-08-03 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_payment_external_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='failure_reason',
            field=models.CharField(max_length=512, null=True),
        ),
    ]
