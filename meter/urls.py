from django.urls import path, include
from .views import list_meters, create_meter, edit_meter, delete_meter, get_token


urlpatterns = [
    path("", list_meters, name="list-meters"),
    path("<int:pk>/edit", edit_meter, name="edit_meter"),
    path("create", create_meter, name="create_meter"),
    path("<int:pk>/delete", delete_meter, name="delete_meter"),
    path("<int:pk>/get-token", get_token, name="get-token"),
]
