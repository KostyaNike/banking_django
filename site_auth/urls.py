from django.urls import path
from site_auth import views

app_name = 'auth'

urlpatterns = [
    path('', views.auth, name='auth'),
    path('login/', views.login, name='login'),
    path('reg/', views.reg, name='reg'),
]