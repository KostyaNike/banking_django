from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, LoginForm
from .models import CustomUser
from django.core.mail import send_mail
from random import randint
from .forms import VerificationForm
from .models import BankCard
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from decimal import Decimal

# Регистрация
def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        print("1")
        if form.is_valid():
            print("2")
            user = form.save(commit=False)
            user.verification_code = ''.join([str(randint(0, 9)) for _ in range(6)])
            user.is_active = False  # Пока не верифицирован, пользователь не активен
            user.save()  # Сохраняем пользователя в базе данных

            # Отправка письма с кодом подтверждения
            send_mail(
                'Код подтверждения',
                f'Ваш код подтверждения: {user.verification_code}',
                'your_email@gmail.com',  # Укажите здесь ваш EMAIL_HOST_USER
                [user.email],
                fail_silently=False,
            )
            return redirect('site_auth:verify')  # Редирект на страницу верификации
    else:
        print("3")
        form = CustomUserCreationForm()
    return render(request, 'site_auth/reg.html', {'form': form})

# Логин
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            return redirect('/home/')
    else:
        form = LoginForm()

    return render(request, 'site_auth/login.html', {'form': form})

# Верификация
def verify(request):
    if request.method == "POST":
        form = VerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            user = CustomUser.objects.filter(verification_code=code).first()
            if user:
                user.is_active = True  # Активируем пользователя
                user.verification_code = None  # Сбрасываем код после успешной верификации
                user.save()

                # Создаем банковскую карту
                bank_card = BankCard(user=user)
                bank_card.generate_card_details()
                bank_card.save()

                return redirect('/home/')
    else:
        form = VerificationForm()
    return render(request, 'site_auth/verify.html', {'form': form})

# Выход
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

# Переадресация на страницу логина
def auth(request):
    return redirect('site_auth:login')
