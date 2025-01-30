from django.db import models
from django.conf import settings
from site_auth.models import BankCard  # Импорт вашей модели карты

class Transaction(models.Model):
    card = models.ForeignKey(BankCard, on_delete=models.CASCADE, related_name="transactions")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=50, choices=[('recharge', 'Поповнення'), ('transfer', 'Переведення')], default='recharge')

    def __str__(self):
        return f"Transaction {self.amount} from card {self.card.card_number} to {self.recipient.username}"
