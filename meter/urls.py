from django.urls import path, include, register_converter
from meter import views as meter_views
from user.utils import HashIdConverter

register_converter(HashIdConverter, "hashid")


urlpatterns = [
    path("", meter_views.MeterListView.as_view(), name="list_meters"),
    path("add", meter_views.MeterCreateView.as_view(), name="add_meter"),
    path("recharge", meter_views.RechargeMeterView.as_view(), name="recharge_meter"),
    path("<hashid:pk>/edit", meter_views.MeterEditView.as_view(), name="edit_meter"),
    path("<hashid:pk>/deactivate", meter_views.deactivate_meter, name="deactivate_meter"),
    path("<hashid:pk>/recharge", meter_views.RechargeMeterView.as_view(), name="recharge_meter"),
    path("manufacturers/add", meter_views.MeterManufacturerCreateView.as_view(), name="add_meter_manufacturer"),
    path("categories/add", meter_views.MeterCategoryCreateView.as_view(), name="add_meter_category"), 
]
