# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from transaction.models import Transaction

# Register your models here.
class TransactionAdmin(admin.ModelAdmin):
    pass

admin.site.register(Transaction, TransactionAdmin)
