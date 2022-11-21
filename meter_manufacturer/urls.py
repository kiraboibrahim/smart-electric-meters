from django.urls import path, register_converter

from prepaid_meters_token_generator_system.converters import HashIdConverter

from meter_manufacturer.views import MeterManufacturerCreateView, MeterManufacturerEditView, MeterManufacturerListView, MeterManufacturerSearchView, MeterManufacturerDeleteView


register_converter(HashIdConverter, "hashid")

urlpatterns = [
    path("", MeterManufacturerListView.as_view(), name="list_meter_manufacturers"),
    path("add", MeterManufacturerCreateView.as_view(), name="add_meter_manufacturer"),
    path("search", MeterManufacturerSearchView.as_view(), name="search_meter_manufacturer"),
    path("<hashid:pk>/delete", MeterManufacturerDeleteView.as_view(), name="delete_meter_manufacturer"),
    path("<hashid:pk>/edit", MeterManufacturerEditView.as_view(), name="edit_meter_manufacturer"),
]
