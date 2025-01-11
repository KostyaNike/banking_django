from datetime import datetime, timedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from random import randint

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Хеширование пароля
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=False)  # Аккаунт становится активным только после верификации
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)  # Добавляем last_login
    verification_code = models.CharField(max_length=6, blank=True, null=True)  # Код верификации
    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email

class BankCard(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="bank_card")
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