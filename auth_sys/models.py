from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
import random
from datetime import datetime, timedelta

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, first_name=None, last_name=None):
        if not phone_number:
            raise ValueError("Необходимо указать номер телефона")
        user = self.model(phone_number=phone_number, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None):
        user = self.create_user(phone_number, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    phone_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"

    @property
    def is_staff(self):
        return self.is_admin

class Card(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="auth_cards"  # Уникальное имя для обратной связи
    )
    card_number = models.CharField(max_length=16, unique=True)
    cvv = models.CharField(max_length=3)
    expiration_date = models.CharField(max_length=5)  # Формат MM/YY
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def generate_card_details(self):
        # Генерация номера карты (начинается с 5 и содержит 16 символов)
        self.card_number = "5" + "".join([str(random.randint(0, 9)) for _ in range(15)])
        # Генерация CVV
        self.cvv = "".join([str(random.randint(0, 9)) for _ in range(3)])
        # Установка срока действия карты (5 лет от текущей даты)
        today = datetime.today()
        expiration_date = today + timedelta(days=5 * 365)
        self.expiration_date = expiration_date.strftime("%m/%y")