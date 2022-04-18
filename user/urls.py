from django.urls import path, register_converter
from user.views import list_users, edit_user, create_user, revoke_password, reset_password, delete_user, profile
from django.contrib.auth import views as auth_views
from user.utils import HashIdConverter

register_converter(HashIdConverter, "hashid")

urlpatterns = [
    path("", list_users, name="list_users"),
    path("login", auth_views.LoginView.as_view(template_name="user/login.html.development"), name="login"),
    path("logout", auth_views.LogoutView.as_view(template_name="user/logout.html.development"), name="logout"),
    path("create", create_user, name="create_user"),
    path("<hashid:pk>/edit", edit_user, name="edit_user"),
    path("<hashid:pk>/revoke_password", revoke_password, name="revoke_password"),
    path("<hashid:pk>/delete", delete_user, name="delete_user"),
    path("password_change", auth_views.PasswordChangeView.as_view(template_name="user/change_password.html.development"), name="password_change"),
    path("password_change/done", auth_views.PasswordChangeDoneView.as_view(template_name="user/change_password_done.html.development"), name="password_change_done"),
    path("forgot_password", reset_password, name="reset_password"),
    path("reset_password_confirm/<uidb64>/<token>", auth_views.PasswordResetConfirmView.as_view(template_name="user/reset_password_confirm.html.development"), name="reset_password_confirm"),
    path("reset_password_complete", auth_views.PasswordResetCompleteView.as_view(template_name="user/reset_password_complete.html.development"), name="password_reset_complete"),
    path("profile", profile, name="dashboard"),
]
