from django.urls import path, register_converter

from prepaid_meters_token_generator_system.utils.converters import HashIdConverter
from meter_category.views import MeterCategoryCreateView


register_converter(HashIdConverter, "hashid")

urlpatterns = [
    path("add", MeterCategoryCreateView.as_view(), name="add_meter_category")
]
