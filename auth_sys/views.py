from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth import login, logout
from .forms import RegistrationForm, LoginForm, VerificationForm
from .models import CustomUser, BankCard
import random

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            send_mail(
                'Код подтверждения',
                f'Ваш код подтверждения: {user.verification_code}',
                'your_email@gmail.com',  # Укажите здесь ваш EMAIL_HOST_USER
                [user.email],
                fail_silently=False,
            )
            user.is_active = False  # Пока не верифицирован, пользователь не активен
            user.save()
            return redirect('/auth/verify')
    else:
        form = RegistrationForm()
    return render(request, 'auth_sys/register.html', {'form': form})

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

                # Создаём банковскую карту
                bank_card = BankCard(user=user)
                bank_card.generate_card_details()
                bank_card.save()

                return redirect('/home/')
    else:
        form = VerificationForm()
    return render(request, 'auth_sys/verify.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = CustomUser.objects.filter(email=email).first()
            if user and user.is_active and user.check_password(password):  # Используем метод проверки пароля
                login(request, user)
                return redirect('/home/')
    else:
        form = LoginForm()
    return render(request, 'auth_sys/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/auth/login')

def home(request):
    user = request.user
    if not user.is_authenticated:  # Проверка на аутентификацию
        return redirect('/auth/login')
    try:
        card = BankCard.objects.get(user=user)
    except BankCard.DoesNotExist:
        card = None
    return render(request, 'auth_sys/home.html', {'user': user, 'card': card})
