from django.shortcuts import render, get_object_or_404
from site_auth.models import BankCard
from money_trans.models import Transaction
from django.contrib import messages
from decimal import Decimal, InvalidOperation  # Подключаем модель транзакций

def cards(request):
    # Получение всех карт, связанных с текущим пользователем
    cards = BankCard.objects.filter(user=request.user)
    context = {
        "cards": cards
    }
    return render(request, "cards/cards.html", context)

def card(request, pk):
    # Получение конкретной карты пользователя
    card = get_object_or_404(BankCard, pk=pk, user=request.user)
    
    transactions = Transaction.objects.filter(card=card).order_by("-date")
    
    context = {
        "card": card,
        "transactions": transactions
    }
    return render(request, "cards/card.html", context)

def mobile_service(request, pk):
    card = get_object_or_404(BankCard, pk=pk, user=request.user)
    if request.method == 'POST':
        phone_number = request.POST['phone_number']
        amount = Decimal(request.POST['amount'])

        # Проверка, достаточно ли средств на карте
        if amount <= card.balance:
            # Создание новой транзакции
            transaction = Transaction.objects.create(
                card=card,
                recipient=request.user,  # Текущий пользователь как получатель
                amount=amount,
                transaction_type='recharge',
                phone_number=phone_number
            )
            # Обновление баланса карты
            card.balance -= amount
            card.save()

            # Уведомление об успешной транзакции
            messages.success(request, 'Поповнення успішне!')
        else:
            messages.error(request, 'Недостатньо коштів для поповнення.')

    return render(request, 'cards/mobile.html', {'card': card})



# from django.shortcuts import render, redirect
# from site_auth.models import BankCard

# def cards(request):
#     cards = BankCard.objects.filter(user = request.user)
#     context = {
#         "cards": cards
#     }
#     return render(request, "cards/cards.html", context)

# def card(request, pk):
#     card = BankCard.objects.get(pk=pk)
#     if request.user != card.user:
#         return redirect("cards")
#     return render(request, "cards/card.html", {
#         "card": card
#     })