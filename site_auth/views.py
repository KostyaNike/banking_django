from database.models import CustomUser, BankCard
from django.shortcuts import redirect, render
from django.core.mail import send_mail
from django.contrib.auth import login, logout
from .forms import RegistrationForm, LoginForm, VerificationForm
from random import randint

def auth(request):
    return render(request, 'site_auth/site_auth.html')

def reg(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.verification_code = ''.join([str(randint(0, 9)) for _ in range(6)])
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
    return render(request, 'site_auth/reg.html', {'form': form})

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
    return render(request, 'site_auth/verify.html', {'form': form})

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
    return render(request, 'site_auth/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return render(request, 'site_auth/logout.html')