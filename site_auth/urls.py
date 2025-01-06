from django.urls import path
from site_auth import views

urlpatterns = [
    path('', views.auth, name='auth'),
]