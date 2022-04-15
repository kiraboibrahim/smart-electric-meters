# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

state_choices = [
    (0, "FAILED"),
    (1, "SUCCESSFUL"),
]

class Transaction(models.Model):
    external_id = models.CharField(max_length=255, unique=True)
    transacted_at = models.DateTimeField(auto_now_add=True)
    charge = models.PositiveIntegerField()
    amount = models.PositiveIntegerField()
    phone_no = models.CharField(max_length=10)
    state = models.IntegerField(choices=state_choices)
