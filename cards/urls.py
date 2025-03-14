from django.urls import path
from cards import views
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

app_name = 'cards'

urlpatterns = [
    path('', views.cards, name='cards'),
    path('<int:pk>/', views.card, name='card'),
    path('<int:pk>/mobile', views.mobile_service, name='mobile_service'),
    path('<int:pk>/transfer', views.transfer, name='transfer'),
    path('<int:pk>/insurance/', TemplateView.as_view(template_name="cards/insurance.html"), name='insurance'),
    path('<int:pk>/insurance/health', views.insurance_health, name='health'),
    path('<int:pk>/insurance/touristic', views.insurance_touristic, name='touristic'),
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
    path('<int:pk>/banka/', TemplateView.as_view(template_name="cards/banka.html"), name='banka'),
    path('<int:pk>/banka/open/', views.open_banka, name='open_banka'),# Страница для открытия новой банки
    path('<int:pk>/banka/my/', views.banka_detail, name='banka_detail'),
    path('<int:pk>/banka/send/', views.bank_transfer, name='bank_transfer'),
    path('<int:pk>/banka/close/', views.close_banka, name='close_banka'),
    path('<int:pk>/add/', views.add_balance, name='add_balance'),
    path('<int:pk>/cashback/', views.cashback, name='cashback'),
    path('remove_cashback/', views.remove_cashback, name='remove_cashback'),
    path('new/', views.open_account, name='open_account'),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])