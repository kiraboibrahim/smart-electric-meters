from django.urls import path, include, re_path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="login"), name="index"),
    re_path(r'^admin/', admin.site.urls),
    path("meters/", include("meter.urls")), 
    path("users/", include("user.urls"))
]
