from django.urls import path, register_converter

from meter_categories.views import MeterCategoryCreateView, MeterCategoryEditView, MeterCategoryDeleteView
from shared.converters import HashIdConverter

register_converter(HashIdConverter, "hashid")

urlpatterns = [
    path("add", MeterCategoryCreateView.as_view(), name="add_meter_category"),
    path("<hashid:meter_category_id>/edit", MeterCategoryEditView.as_view(), name="edit_meter_category"),
    path("<hashid:meter_category_id>/delete", MeterCategoryDeleteView.as_view(), name="delete_meter_category")
]
