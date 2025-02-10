from django.db import models
from random import randint
from datetime import datetime, timedelta
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    credit_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.email

class BankCard(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bank_cards")
    card_number = models.CharField(max_length=16, unique=True)
    cvv = models.CharField(max_length=3)
    expiry_date = models.CharField(max_length=5)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def generate_card_details(self):
        self.card_number = f"5{''.join([str(randint(0, 9)) for _ in range(15)])}"
        self.cvv = f"{randint(100, 999)}"
        self.expiry_date = (datetime.now() + timedelta(days=5 * 365)).strftime("%m/%y")

    def __str__(self):
        return f"Card {self.card_number} for {self.user.email}"
