from django.contrib import admin
from django.conf import settings
from django.urls import path, include, re_path
from django.views.generic import RedirectView

from users import api_views as users_api_views

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="login"), name="index"),
    path("meters/", include("meters.urls")),
    path("users/", include("users.urls")),
    path("vendors/", include("meter_vendors.urls")),
    path("recharge-tokens/", include("recharge_tokens.urls"))
]

api_urlpatterns = [
    path("api/users", users_api_views.UserListAPIView.as_view(), name="api_user_list")
]

if settings.DEBUG:
    urlpatterns.append(re_path(r'^admin/', admin.site.urls))

urlpatterns += api_urlpatterns
