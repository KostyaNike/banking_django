from django.urls import path
from . import views

app_name = 'site_auth'

urlpatterns = [
    path('', views.auth, name='auth'),
    path('register/', views.register_view, name='register'),  # Страница регистрации
    path('login/', views.login_view, name='login'),   # Страница логина
    path('verify/', views.verify, name='verify'),     # Страница верификации
    path('logout/', views.logout_view, name='logout'), # Страница выхода
]