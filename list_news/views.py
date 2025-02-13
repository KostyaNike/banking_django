from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import News

# Главная страница с новостями
def news_list(request):
    return render(request, 'home/news_list.html')

# Загрузка новостей по частям (по 9 новостей за раз)
def load_news(request):
    offset = int(request.GET.get('offset', 0))  # Начальный индекс
    limit = 9  # Количество новостей за раз

    # Получаем новости, сортируем по дате
    news = News.objects.all().order_by('-published_at')[offset:offset + limit]

    # Формируем данные для отправки в JSON
    news_data = [
        {
            'id': item.id,
            'title': item.title,
            'description': item.description[:100] + '...',  # Короткое описание
            'image_url': item.image_url,
            'published_at': item.published_at.strftime('%Y-%m-%d %H:%M'),  # Форматируем дату
            'link': item.link
        }
        for item in news
    ]

    return JsonResponse({'news': news_data})

# Страница с подробным отображением новости
def news_detail(request, id):
    # Получаем новость по id
    news = get_object_or_404(News, id=id)
    return render(request, 'home/news_page.html', {'news': news})