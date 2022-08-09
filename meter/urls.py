from django.urls import path, include, register_converter

from prepaid_meters_token_generator_system.utils.converters import HashIdConverter
from meter import views as meter_views

register_converter(HashIdConverter, "hashid")


urlpatterns = [
    path("", meter_views.MeterListView.as_view(), name="list_meters"),
    path("add", meter_views.MeterCreateView.as_view(), name="add_meter"),
    path("recharge", meter_views.RechargeMeterView.as_view(), name="recharge_meter"),
    path("search", meter_views.MeterSearchView.as_view(), name="search_meters"),
    path("<hashid:pk>/edit", meter_views.MeterEditView.as_view(), name="edit_meter"),
    path("<hashid:pk>/deactivate", meter_views.deactivate_meter, name="deactivate_meter"),
    path("<hashid:pk>/recharge", meter_views.RechargeMeterView.as_view(), name="recharge_meter"),
    path("manufacturers/", meter_views.MeterManufacturerListView.as_view(), name="list_meter_manufacturers"),
    path("manufacturers/add", meter_views.MeterManufacturerCreateView.as_view(), name="add_meter_manufacturer"),
    path("manufacturers/<hashid:pk>/edit", meter_views.MeterManufacturerEditView.as_view(), name="edit_meter_manufacturer"),
    path("categories/add", meter_views.MeterCategoryCreateView.as_view(), name="add_meter_category"), 
]
