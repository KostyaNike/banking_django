from django.shortcuts import render, get_object_or_404
from site_auth.models import BankCard
from money_trans.models import Transaction  # Подключаем модель транзакций

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
    
    # Получение транзакций, связанных с этой картой
    transactions = Transaction.objects.filter(card=card).order_by("-date")
    
    context = {
        "card": card,
        "transactions": transactions
    }
    return render(request, "cards/card.html", context)



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