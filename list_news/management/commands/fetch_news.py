import requests
from django.core.management.base import BaseCommand
from list_news.models import News

class Command(BaseCommand):
    help = 'Fetches news from an external API and saves it to the database'

    def handle(self, *args, **kwargs):
        # URL API для получения новостей с украинских источников на украинском языке
        url = 'https://newsapi.org/v2/top-headlines?country=ua&apiKey=da57a940fa9d41018c1ff8af6f12b4fd'
        
        # Выполняем запрос к API
        response = requests.get(url)
        
        # Проверяем успешность запроса
        if response.status_code == 200:
            news_data = response.json()

            # Печатаем структуру данных для проверки
            print(news_data)

            # Проверяем, есть ли ключ 'articles' в данных
            if 'articles' in news_data:
                for article in news_data['articles']:
                    title = article.get('title', '')
                    description = article.get('description', '')
                    image_url = article.get('urlToImage', '')
                    published_at = article.get('publishedAt', '')
                    link = article.get('url', '')

                    # Сохранение новостей в БД
                    News.objects.create(
                        title=title,
                        description=description,
                        image_url=image_url,
                        published_at=published_at,
                        link=link
                    )

                self.stdout.write(self.style.SUCCESS('Successfully fetched and saved news.'))
            else:
                self.stdout.write(self.style.ERROR('No articles found in the response.'))
        else:
            self.stdout.write(self.style.ERROR('Failed to fetch news from API. Status code: {}'.format(response.status_code)))