from database.models import BankCard
from django.shortcuts import render

def home(request):
    user = request.user
    if not user.is_authenticated:  # Проверка на аутентификацию
        card = None
    else:
        try:
            card = BankCard.objects.get(user=user)
        except BankCard.DoesNotExist:
            card = None
    return render(
        request,
        'home/home.html',
        {
            'is_authenticated': False,
            'user': user,
            'card': card
        }
    )