from django.urls import path, register_converter
from user.views import ResetPassword, UserListView, UserCreateView, UserEditView, UserProfileEditView, UnitPriceEditView, revoke_password, delete_user, dashboard, profile
from django.contrib.auth import views as auth_views
from user.utils import HashIdConverter

register_converter(HashIdConverter, "hashid")

urlpatterns = [
    path("", UserListView.as_view(), name="list_users"),
    path("login", auth_views.LoginView.as_view(template_name="user/login.html.development"), name="login"),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
    path("prices/<hashid:pk>/edit", UnitPriceEditView.as_view(), name="edit_unit_price"),
    path("register", UserCreateView.as_view(), name="register_user"),
    path("<hashid:pk>/edit", UserEditView.as_view(), name="edit_user"),
    path("<hashid:pk>/revoke-password", revoke_password, name="revoke_password"),
    path("<hashid:pk>/delete", delete_user, name="delete_user"),
    path("password-change", auth_views.PasswordChangeView.as_view(template_name="user/change_password.html.development"), name="password_change"),
    path("password-change/done", auth_views.PasswordChangeDoneView.as_view(template_name="user/change_password_done.html.development"), name="password_change_done"),
    path("forgot-password", ResetPassword.as_view(), name="forgot_password"),
    path("reset-password-confirm/<uidb64>/<token>", auth_views.PasswordResetConfirmView.as_view(template_name="user/reset_password_confirm.html.development"), name="reset_password_confirm"),
    path("reset-password-complete", auth_views.PasswordResetCompleteView.as_view(template_name="user/reset_password_complete.html.development"), name="reset_password_complete"),
    path("dashboard", dashboard, name="dashboard"),
    path("profile", profile, name="profile"),
    path("profile/edit", UserProfileEditView.as_view(), name="edit_user_profile"),
]
