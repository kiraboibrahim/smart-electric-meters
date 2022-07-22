from django.urls import path, include, register_converter
from meter.views import MeterListView, MeterCreateView, MeterEditView, MeterCategoryCreateView, MeterManufacturerCreateView, BuyTokenView, delete_meter, unlink_meter
from user.utils import HashIdConverter

register_converter(HashIdConverter, "hashid")


urlpatterns = [
    path("", MeterListView.as_view(), name="list_meters"),
    path("register", MeterCreateView.as_view(), name="register_meter"),
    path("buy-token", BuyTokenView.as_view(), name="buy_token"),
    path("<hashid:pk>/edit", MeterEditView.as_view(), name="edit_meter"),
    path("<hashid:pk>/delete", delete_meter, name="delete_meter"),
    path("<hashid:pk>/buy-token", BuyTokenView.as_view(), name="buy_token"),
    path("<hashid:pk>/unlink", unlink_meter, name="unlink_meter"),
    path("manufacturers/register", MeterManufacturerCreateView.as_view(), name="register_meter_manufacturer"),
    path("categories/register", MeterCategoryCreateView.as_view(), name="register_meter_category"), 
]
