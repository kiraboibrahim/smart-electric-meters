from django.urls import path, include, register_converter
from .views import list_meters, register_meter, edit_meter, delete_meter, buy_token
from user.utils import HashIdConverter

register_converter(HashIdConverter, "hashid")


urlpatterns = [
    path("", list_meters, name="list_meters"),
    path("<hashid:pk>/edit", edit_meter, name="edit_meter"),
    path("register", register_meter, name="register_meter"),
    path("<hashid:pk>/delete", delete_meter, name="delete_meter"),
    path("<hashid:pk>/buy_token", buy_token, name="buy_token"),
]
