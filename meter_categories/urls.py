from django.urls import path, register_converter

from shared.converters import HashIdConverter
from meter_categories.views import MeterCategoryCreateView


register_converter(HashIdConverter, "hashid")

urlpatterns = [
    path("add", MeterCategoryCreateView.as_view(), name="add_meter_category")
]
