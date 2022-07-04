from django.conf.urls import url
from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", auth_views.LoginView.as_view(template_name="user/login.html.development"), name="home"),
    url(r'^admin/', admin.site.urls),
    path("meters/", include("meter.urls")), 
    path("users/", include("user.urls"))
]
