from django.urls import path
from site_auth import views

app_name = 'auth'

urlpatterns = [
    path('', views.auth, name='auth'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('reg/', views.reg, name='reg'),
    path('verify/', views.verify, name='verify'),
]