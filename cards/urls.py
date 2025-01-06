from django.urls import path
from cards import views

urlpatterns = [
    path('', views.cards, name='cards'),
    path('card/', views.card, name='card'),
]