from django.urls import path, include, re_path
from django.contrib import admin
from django.views.generic import RedirectView


urlpatterns = [
    path("", RedirectView.as_view(pattern_name="login"), name="index"),
    re_path(r'^admin/', admin.site.urls),
    path("meters/", include("meters.urls")),
    path("users/", include("users.urls")),
    path("manufacturers/", include("manufacturers.urls")),
    path("categories/", include("meter_categories.urls")),
    path("payments/", include("payments.urls")),
    path("recharge-tokens/", include("recharge_tokens.urls"))
]
