from django.urls import path
from .views import news_list, news_detail, load_news
from . import views

urlpatterns = [
    path('news/', views.news_list, name='news_list'),
    path('load_news/', views.load_news, name='load_news'),
    path('news/<int:id>/', views.news_detail, name='news_detail'),
]