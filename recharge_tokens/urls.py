from django.urls import path

from .views import RechargeTokenOrderListView

urlpatterns = [
    path("orders", RechargeTokenOrderListView.as_view(), name="recharge_token_order_list"),
]
