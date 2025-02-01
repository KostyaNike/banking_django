from django.shortcuts import render, get_object_or_404, redirect
from site_auth.models import BankCard, CustomUser
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

def transfer(request, pk):
    card = get_object_or_404(BankCard, pk=pk, user=request.user)
    if request.method == 'POST':
        card_number = request.POST['card_number']
        card_2 = get_object_or_404(BankCard, card_number=int(card_number))
        amount = Decimal(request.POST['amount'])
        # Проверка, достаточно ли средств на карте
        if card != card_2:
            if amount <= card.balance:
                # Создание новой транзакции
                transaction = Transaction.objects.create(
                    card=card,
                    recipient=get_object_or_404(CustomUser, id=card_2.user_id),  # Текущий пользователь как получатель
                    amount=amount,
                    transaction_type='recharge',
                    phone_number=card_number
                )
                # Обновление баланса карты
                card_2.balance += amount
                card_2.save()
                card.balance -= amount
                card.save()
                # Уведомление об успешной транзакции
                messages.success(request, 'Успешный перевод!')
            else:
                messages.error(request, 'Недостатньо коштів для перевода.')
        else:
            messages.error(request, 'Нельзя перевести деньги самому себе.')
    return render(request, 'cards/transfer.html', {'card': card})