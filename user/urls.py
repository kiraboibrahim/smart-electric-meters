from django.urls import path, register_converter
from user.views import list_users, edit_user, create_user, revoke_password, reset_password_request, profile
from django.contrib.auth import views
from user.utils import HashIdConverter

register_converter(HashIdConverter, "hashid")

urlpatterns = [
    path("", list_users, name="list-users"),
    path("login", views.LoginView.as_view(template_name="user/login.html.development"), name="login"),
    path("logout", views.LogoutView.as_view(template_name="user/logout.html.development"), name="logout"),
    path("create", create_user, name="create_user"),
    path("<hashid:pk>/edit", edit_user, name="edit_user"),
    path("<hashid:pk>/change_password", revoke_password, name="revoke_password"),
    path("password_change", views.PasswordChangeView.as_view(template_name="user/change_password.html.development"), name="password_change"),
    path("password_change/done", views.PasswordChangeDoneView.as_view(template_name="user/change_password_done.html.development"), name="password_change_done"),
    path("profile", profile, name="dashboard"),
]
