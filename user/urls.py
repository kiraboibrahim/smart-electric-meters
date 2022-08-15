from django.urls import path, register_converter
from django.contrib.auth import views as auth_views

from prepaid_meters_token_generator_system.utils.converters import HashIdConverter
from user import views as user_views


register_converter(HashIdConverter, "hashid")

urlpatterns = [
    path("", user_views.UserListView.as_view(), name="list_users"),
    path("login", auth_views.LoginView.as_view(template_name="user/login.html.development"), name="login"),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
    path("search", user_views.UserSearchView.as_view(), name="search_users"),
    path("prices/<hashid:pk>/edit", user_views.UnitPriceEditView.as_view(), name="edit_unit_price"),
    path("add", user_views.UserCreateView.as_view(), name="add_user"),
    path("<hashid:pk>/edit", user_views.UserEditView.as_view(), name="edit_user"),
    path("<hashid:pk>/delete", user_views.UserDeleteView.as_view(), name="delete_user"),
    path("password-change", auth_views.PasswordChangeView.as_view(template_name="user/change_password.html.development"), name="password_change"),
    path("password-change/done", auth_views.PasswordChangeDoneView.as_view(template_name="user/change_password_done.html.development"), name="password_change_done"),
    path("forgot-password", user_views.ResetPassword.as_view(), name="forgot_password"),
    path("reset-password-confirm/<uidb64>/<token>", auth_views.PasswordResetConfirmView.as_view(template_name="user/reset_password_confirm.html.development"), name="password_reset_confirm"),
    path("reset-password-complete", auth_views.PasswordResetCompleteView.as_view(template_name="user/reset_password_complete.html.development"), name="password_reset_complete"),
    path("dashboard", user_views.dashboard, name="dashboard"),
    path("profile", user_views.profile, name="profile"),
    path("profile/edit", user_views.UserProfileEditView.as_view(), name="edit_user_profile"),
]
