from django.urls import path
from . import views

app_name = "auth_sys"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("verify/", views.verify, name="verify"),
    path("login/", views.login_view, name="login"),
]