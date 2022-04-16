# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from meter.utils import is_admin_or_super_admin
from transaction.models import Transaction

# Create your views here.

@user_passes_test(is_admin_or_super_admin)
def list_transactions(request):
    transactions = Transaction.objects.all()
    return render(request, "transaction/list_transactions.html.development", {"transactions": transactions})
    
