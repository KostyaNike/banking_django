from django.shortcuts import render

def cards(request):
    return render(request, 'cards/cards.html', {
        'is_authenticated': False,
        'cards': []
    })

def card(request):
    return render(request, 'cards/card.html', {
        'first_name': 'name',
        'last_name': 'last_name',
        'is_authenticated': False,
        'card_title': 'card_1',
        'card_number': '0000 0000 0000 0000',
        'cvv': '000',
        'expiration_date': '00.00.0000',
        'balance': 0,
    })