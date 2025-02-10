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
    path('<int:pk>/train/', views.search_trains, name='search_trains'),  
    path('<int:pk>/auto/', TemplateView.as_view(template_name="cards/auto.html"), name='auto'),
    path('<int:pk>/auto/auto_parking/', views.auto_parking, name='auto_parking'),
    path('<int:pk>/auto/auto_fine/', TemplateView.as_view(template_name="cards/auto_fine.html"), name='auto_fine'),
    path('<int:pk>/auto/auto_fine/auto_fine_parking/', views.check_auto_fines, name='auto_fine_parking'),
    path('<int:pk>/auto/auto_fine/auto_pdr/', views.check_auto_fines_pdr, name='auto_pdr'),
    path('<int:pk>/credit/add_credit/', views.credit_view, name='add_credit'),
    path('<int:pk>/credit/', TemplateView.as_view(template_name="cards/credit.html"), name='credit'),
    path('<int:pk>/credit/info/', views.credit_info, name='credit_info'),
]