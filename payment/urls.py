from django.urls import path

from payment.views import PaymentListView, PaymentSearchView

urlpatterns = [
    path("", PaymentListView.as_view(), name="list_payments"),
    path("search", PaymentSearchView.as_view(), name="search_payments"),
]
