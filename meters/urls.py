from django.urls import path

from . import views as meter_views

urlpatterns = [
    path("", meter_views.MeterListView.as_view(), name="meter_list"),
    path("create", meter_views.MeterCreateView.as_view(), name="meter_create"),
    path("<hashid:pk>/edit", meter_views.MeterUpdateView.as_view(), name="meter_update"),
    path("<hashid:pk>/recharge", meter_views.MeterRechargeView.as_view(), name="meter_recharge"),
    path("<hashid:pk>/deactivate", meter_views.MeterDeactivateView.as_view(), name="meter_deactivate"),
    path("<hashid:pk>/activate", meter_views.MeterActivateView.as_view(), name="meter_activate"),
]
