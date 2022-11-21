from django.urls import path

from .views import RechargeTokenListView


urlpatterns = [
    path("", RechargeTokenListView.as_view(), name="list_recharge_tokens"),
]
