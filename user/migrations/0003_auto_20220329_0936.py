# Generated by Django 2.2.24 on 2022-03-29 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20220329_0906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prepaidmeteruser',
            name='acc_type',
            field=models.PositiveIntegerField(choices=[(1, 'Super Admin'), (2, 'Admin'), (4, 'Manager')]),
        ),
        migrations.AlterField(
            model_name='prepaidmeteruser',
            name='phone_no',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
