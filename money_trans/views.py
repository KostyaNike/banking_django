from django.shortcuts import render, get_object_or_404
from cards.models import BankCard
from .models import Transaction
from django.db.models import Sum
from decimal import Decimal

def card_transactions(request, card_number):
    # Получаем карту
    card = get_object_or_404(BankCard, card_number=card_number, user=request.user)
    transactions = Transaction.objects.filter(card=card)  # Только транзакции для этой карты

    # Вычисляем сумму и количество
    total_amount = transactions.aggregate(total=Sum('amount'))['total'] or Decimal(0)
    total_count = transactions.count()

    # Передаем данные в шаблон
    return render(request, "cards/card.html", {
        "card": card,
        "transactions": transactions,
        "total_amount": total_amount,
        "total_count": total_count,
    })