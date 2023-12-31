# Generated by Django 3.2.19 on 2023-08-16 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField()),
                ('status', models.PositiveIntegerField(choices=[(1, 'PENDING'), (2, 'FAILED'), (3, 'SUCCESSFUL')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('external_id', models.CharField(max_length=255, null=True, unique=True)),
                ('failure_reason', models.CharField(max_length=512, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
