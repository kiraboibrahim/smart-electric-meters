from django.urls import path
from django.contrib.auth import views as auth_views

from . import views as user_views
from .forms import AuthenticationForm


urlpatterns = [
    path("", user_views.UserListView.as_view(), name="user_list"),
    path("login", auth_views.LoginView.as_view(template_name="users/login.html", form_class=AuthenticationForm, redirect_authenticated_user=True), name="login"),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
    path("create", user_views.UserCreateView.as_view(), name="user_create"),
    path("<hashid:pk>/update", user_views.UserUpdateView.as_view(), name="user_update"),
    path("<hashid:pk>/delete", user_views.UserDeleteView.as_view(), name="user_delete"),
    path("forgot-password", user_views.PasswordResetView.as_view(), name="password_forgot"),
    path("reset-password-confirm/<uidb64>/<token>",
         auth_views.PasswordResetConfirmView.as_view(template_name="users/password_reset_confirm.html"),
         name="password_reset_confirm"),
    path("reset-password-complete",
         auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
         name="password_reset_complete"),
    path("change-password", user_views.MyPasswordChangeView.as_view(), name="password_update"),
    path("dashboard", user_views.MyDashboardView.as_view(), name="dashboard"),
    path("profile", user_views.MyProfileView.as_view(), name="profile"),
    path("profile/update", user_views.MyProfileUpdateView.as_view(), name="user_profile_update"),
    path("prices/update", user_views.MyUnitPriceUpdateView.as_view(), name="unit_price_update"),
]
