from django.urls import path

from .views import RechargeTokenListView, RechargeTokenSearchView

urlpatterns = [
    path("", RechargeTokenListView.as_view(), name="list_recharge_tokens"),
    path("search", RechargeTokenSearchView.as_view(), name="search_recharge_tokens"),
]
