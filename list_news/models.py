from django.db import models

class News(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.URLField()
    published_at = models.DateTimeField()
    link = models.URLField()

    def __str__(self):
        return self.title