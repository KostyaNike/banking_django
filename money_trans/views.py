from django.shortcuts import render, get_object_or_404
from cards.models import BankCard
from .models import Transaction

def card_transactions(request, card_number):
    # Получаем карту по номеру
    card = get_object_or_404(BankCard, card_number=card_number, user=request.user)
    # Все транзакции для данной карты
    transactions = card.transactions.all()
    return render(request, "money_trans/transactions.html", {
        "card": card,
        "transactions": transactions,
    })
