from django.urls import path

from . import views as meter_vendor_views

urlpatterns = [
    path("", meter_vendor_views.MeterVendorListView.as_view(), name="meter_vendor_list"),
    path("create", meter_vendor_views.MeterVendorCreateView.as_view(), name="meter_vendor_create"),
    path("<hashid:pk>/delete", meter_vendor_views.MeterVendorDeleteView.as_view(), name="meter_vendor_delete"),
    path("<hashid:pk>/update", meter_vendor_views.MeterVendorUpdateView.as_view(), name="meter_vendor_update"),
]
