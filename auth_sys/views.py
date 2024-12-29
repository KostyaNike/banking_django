from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegistrationForm, VerificationForm, LoginForm
from .models import User, Card
from account.models import Account
import random
from twilio.rest import Client
from django.conf import settings
from auth_sys.models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

# Хранилище кодов подтверждения
verification_codes = {}

def send_sms(phone_number, code):
    account_sid = 'ACa881a17e19899848815e2788cb94b843'  # Ваш Twilio SID
    auth_token = 'c96ea8d6ae78ede4a1f38e43d57319d6'    # Ваш Twilio токен
    from_number = '+1 231 634 6360'  # Ваш Twilio номер

    client = Client(account_sid, auth_token)
    client.messages.create(
        body=f"Ваш код подтверждения: {code}",
        from_=from_number,
        to=phone_number
    )

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data["phone_number"]
            password = form.cleaned_data["password"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]

            # Проверяем, существует ли уже пользователь с таким номером телефона
            if User.objects.filter(phone_number=phone_number).exists():
                form.add_error('phone_number', 'Этот номер телефона уже зарегистрирован.')
            else:
                # Генерация и отправка кода подтверждения
                code = "".join([str(random.randint(0, 9)) for _ in range(6)])
                verification_codes[phone_number] = code
                send_sms(phone_number, code)

                # Сохраняем данные в сессии для дальнейшего использования
                request.session["phone_number"] = phone_number
                request.session["first_name"] = first_name
                request.session["last_name"] = last_name
                request.session["password"] = password

                # Перенаправляем на страницу верификации
                return redirect("auth_sys:verify")
    else:
        form = RegistrationForm()

    return render(request, "auth_sys/register.html", {"form": form})

def verify(request):
    phone_number = request.session.get("phone_number")
    if not phone_number:
        return redirect("auth_sys:register")

    if request.method == "POST":
        form = VerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]

            if verification_codes.get(phone_number) == code:
                # Удаляем код после успешной верификации
                del verification_codes[phone_number]

                # Получаем данные из сессии
                first_name = request.session.get("first_name")
                last_name = request.session.get("last_name")
                password = request.session.get("password")

                # Создаем пользователя
                user_model = get_user_model()
                user = user_model.objects.create_user(
                    phone_number=phone_number, 
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )

                # Создание карточки для пользователя
                card = Card(user=user)
                card.generate_card_details()  # Генерация номера карты, CVV и срока действия
                card.save()

                # Создание аккаунта
                account = Account(user=user, balance=0, linked_card=card)
                account.save()

                # Логиним пользователя
                login(request, user)

                # Перенаправляем на домашнюю страницу
                return redirect("home")
            else:
                form.add_error("code", "Неверный код")
    else:
        form = VerificationForm()

    return render(request, "auth_sys/verify.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            password = form.cleaned_data["password"]

            try:
                user = User.objects.get(first_name=first_name, last_name=last_name)
                if user.check_password(password):
                    login(request, user)
                    return redirect("home")
            except User.DoesNotExist:
                form.add_error(None, "Пользователь не найден")
    else:
        form = LoginForm()

    return render(request, "auth_sys/login.html", {"form": form})
