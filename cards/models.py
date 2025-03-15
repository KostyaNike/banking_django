from django.db import models
from django.conf import settings
import uuid
from django.core.exceptions import ValidationError

def validate_goal(value):
    if value > 100000:
        raise ValidationError('Ціль накопичування не може перевищувати 100000 грн.')

class Banka(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='banka')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deposit_count = models.IntegerField(default=0)
    opening_date = models.DateTimeField(auto_now_add=True)
    closing_date = models.DateTimeField(null=True, blank=True)
    description = models.TextField()
    name = models.CharField(max_length=255)
    hash_code = models.CharField(max_length=12, unique=True, default=uuid.uuid4().hex[:12])
    goal = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[validate_goal]  # Добавляем валидатор для поля goal
    )

    def __str__(self):
        return f'{self.name} ({self.user.email})'

class UserCashback(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cashback")  # Связь с пользователем
    cafe_restaurants = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Кафе та ресторани
    kids_stores = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Дитячі магазини
    e_scooters = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Електросамокати
    cinemas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Кінотеатри
    transport = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Проїзд
    mobile_recharge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Поповнення мобільного
    parking = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Парковка
    max_cashback = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Максимальный кешбэк

    def get_total_cashback(self):
        return (
            self.cafe_restaurants +
            self.kids_stores +
            self.e_scooters +
            self.cinemas +
            self.transport +
            self.mobile_recharge +
            self.parking
        )

    def get_cashback_percentage(self):
        if self.max_cashback > 0:
            return (self.get_total_cashback() / self.max_cashback) * 100
        return 0

    def __str__(self):
        return f"Cashback for {self.user.email}"
