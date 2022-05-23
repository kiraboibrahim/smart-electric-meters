from django.urls import path, include, register_converter
from meter.views import buy_token, MeterListView, MeterCreateView, MeterEditView, delete_meter, MeterCategoryCreateView
from user.utils import HashIdConverter

register_converter(HashIdConverter, "hashid")


urlpatterns = [
    path("", MeterListView.as_view(), name="list_meters"),
    path("category/register", MeterCategoryCreateView.as_view(), name="register_meter_category"), 
    path("<hashid:pk>/edit", MeterEditView.as_view(), name="edit_meter"),
    path("register", MeterCreateView.as_view(), name="register_meter"),
    path("<hashid:pk>/delete", delete_meter, name="delete_meter"),
    path("<hashid:pk>/buy_token", buy_token, name="buy_token"),
]
