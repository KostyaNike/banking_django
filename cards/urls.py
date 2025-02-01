from django.urls import path
from cards import views
from django.views.generic import TemplateView

app_name = 'cards'

urlpatterns = [
    path('', views.cards, name='cards'),
    path('<int:pk>/', views.card, name='card'),
    path('<int:pk>/mobile', views.mobile_service, name='mobile_service'),
    path('<int:pk>/transfer', views.transfer, name='transfer'),
    path('<int:pk>/insurance/', TemplateView.as_view(template_name="cards/insurance.html"), name='insurance'),
    path('<int:pk>/close-card/', views.delete_card, name='close_card'),
]