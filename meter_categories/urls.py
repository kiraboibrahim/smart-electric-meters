from django.urls import path, register_converter

from meter_categories.views import MeterCategoryCreateView
from shared.converters import HashIdConverter

register_converter(HashIdConverter, "hashid")

urlpatterns = [
    path("add", MeterCategoryCreateView.as_view(), name="add_meter_category")
]
