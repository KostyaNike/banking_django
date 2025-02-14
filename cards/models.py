from django.db import models
from django.conf import settings
import uuid

class Banka(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='banka')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deposit_count = models.IntegerField(default=0)
    opening_date = models.DateTimeField(auto_now_add=True)
    closing_date = models.DateTimeField(null=True, blank=True)
    description = models.TextField()
    name = models.CharField(max_length=255)
    hash_code = models.CharField(max_length=12, unique=True, default=uuid.uuid4().hex[:12])

    def __str__(self):
        return f'{self.name} ({self.user.email})'