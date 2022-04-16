from django.urls import path
from transaction.views import list_transactions

urlpatterns = [
    path("history", list_transactions, name="transaction-history"), 
]
