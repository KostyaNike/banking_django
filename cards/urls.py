from django.urls import path
from cards import views

urlpatterns = [
    path('', views.cards, name='cards'),
    path('<int:pk>/', views.card, name='card'),
    path('<int:pk>/mobile', views.mobile_service, name='mobile_service'),
    path('<int:pk>/transfer', views.transfer, name='transfer'),
]