from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Card(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="account_cards"  # Уникальное имя для обратной связи
    )
    card_number = models.CharField(max_length=16, unique=True)
    cvv = models.CharField(max_length=3)
    expiration_date = models.CharField(max_length=5)  # Формат: MM/YY

    def __str__(self):
        return f"Card {self.card_number} ({self.user.phone_number})"


class Account(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="account")
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    linked_card = models.OneToOneField(Card, on_delete=models.CASCADE, related_name="account")

    def __str__(self):
        return f"Account {self.user.phone_number} - Balance: {self.balance}"