from django.shortcuts import render, get_object_or_404, redirect
from site_auth.models import BankCard, CustomUser
from money_trans.models import Transaction
from django.contrib import messages
from decimal import Decimal, InvalidOperation  # Подключаем модель транзакций
import feedparser
from .gtfs_processor import get_routes
import re
from django.contrib.auth.decorators import login_required

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

def delete_card(request, pk):
    card = get_object_or_404(BankCard, pk=pk, user=request.user)
    if request.method == 'POST':
        card.delete()
        messages.success(request, "Картка успішно відалена.")
        return redirect('cards:cards')  # Перенаправление на список карт
    return render(request, 'cards/close_card.html', {'card': card})

def get_train_routes_gtfs(departure, arrival, date):
    # Пример URL для GTFS-данных (замените на актуальный URL для нужной страны)
    gtfs_feed_url = "https://gtfs.org/"  # Укажите настоящий URL GTFS

    # Загружаем GTFS feed
    feed = feedparser.parse(gtfs_feed_url)
    routes = []

    for entry in feed.entries:
        # Фильтруем по отправлению и прибытию
        if departure.lower() in entry.title.lower() and arrival.lower() in entry.title.lower():
            routes.append({
                "train_number": entry.title,
                "departure_time": entry.published,
                "arrival_time": entry.updated,
                "duration": entry.duration,
                "link": entry.link
            })

    return routes

def search_trains(request, pk):
    # Получаем карту по pk
    card = get_object_or_404(BankCard, pk=pk, user=request.user)
    
    routes = None
    if request.method == "POST":
        departure = request.POST.get("departure")
        arrival = request.POST.get("arrival")
        date = request.POST.get("date")
        routes = get_routes(departure, arrival, date)

    return render(request, "cards/train.html", {"routes": routes, 'card': card})

def auto_parking(request, pk):
    card = get_object_or_404(BankCard, pk=pk, user=request.user)

    if request.method == 'POST':
        city = request.POST.get('city')
        car_number = request.POST.get('car_number')

        # Регулярное выражение для украинского номера
        car_number_pattern = r'^[A-Z]{2}[0-9]{4}[A-Z]{2}$'

        # Проверка формата номера
        if not re.match(car_number_pattern, car_number):
            error_message = 'Номер автомобиля должен быть в формате XX0000XX (например, AB1234CD).'
            return render(request, 'cards/auto_parking.html', {'card': card, 'error_message': error_message})

        # Стоимость парковки
        parking_fee = Decimal('150.00')

        # Проверка баланса на карте
        if card.balance >= parking_fee:
            try:
                # Ищем пользователя "Автомобільна служба" (если его нет, создаём)
                auto_service_user, created = CustomUser.objects.get_or_create(
                    username="auto_service",
                    defaults={"first_name": "Автомобільна", "last_name": "служба"}
                )

                # Создаём транзакцию
                transaction = Transaction.objects.create(
                    card=card,
                    recipient=auto_service_user,  # Передаём объект пользователя
                    amount=parking_fee,
                    transaction_type='auto_parking'
                )

                # Обновляем баланс карты
                card.balance -= parking_fee
                card.save()

                success_message = 'Оплата прошла успешно!'
                return render(request, 'cards/auto_parking.html', {'card': card, 'success_message': success_message})

            except Exception as e:
                error_message = f'Ошибка транзакции: {str(e)}'
                return render(request, 'cards/auto_parking.html', {'card': card, 'error_message': error_message})

        else:
            error_message = 'Недостаточно средств на карте.'
            return render(request, 'cards/auto_parking.html', {'card': card, 'error_message': error_message})

    return render(request, 'cards/auto_parking.html', {'card': card})

def check_auto_fines(request, pk):
    message = None

    if request.method == 'POST':
        car_number = request.POST.get('car_number')

        # Регулярное выражение для украинских номеров
        car_number_pattern = r'^[A-Z]{2}[0-9]{4}[A-Z]{2}$'

        if not re.match(car_number_pattern, car_number):
            message = "Номер автомобіля має бути у форматі XX0000XX (наприклад, AB1234CD)."
        else:
            message = "Жодний штраф не зареєстровано на це авто."

    return render(request, 'cards/auto_fine_parking.html', {'message': message})

def check_auto_fines_pdr(request, pk):
    message = None

    if request.method == 'POST':
        car_number = request.POST.get('car_number')

        # Регулярное выражение для украинских номеров
        car_number_pattern = r'^[A-Z]{2}[0-9]{4}[A-Z]{2}$'

        if not re.match(car_number_pattern, car_number):
            message = "Номер автомобіля має бути у форматі XX0000XX (наприклад, AB1234CD)."
        else:
            message = "Жодний штраф не зареєстровано на це авто."

    return render(request, 'cards/auto_pdr.html', {'message': message})

@login_required
def credit_view(request, pk):
    card = get_object_or_404(BankCard, pk=pk, user=request.user)
    user = request.user

    # Получаем данные из сессии, если они есть
    credit_term = request.session.get("credit_term", 0)
    monthly_payment = request.session.get("monthly_payment", None)

    if request.method == "POST":
        # Оформление кредита
        if "take_credit" in request.POST:
            credit_amount = Decimal(request.POST.get("credit_amount"))
            credit_term = int(request.POST.get("credit_term"))

            if credit_amount < 500 or credit_amount > 50000:
                messages.error(request, "Сума кредиту повинна бути в межах від 500 до 50000.")
                return redirect("cards:add_credit", pk=pk)

            # Определяем процентную ставку
            interest_rate = Decimal(0.15) if credit_term <= 6 else Decimal(0.20)
            total_payment = credit_amount * (1 + interest_rate)
            monthly_payment = round(total_payment / credit_term, 2)

            # Сохраняем в пользователя и сессию
            user.credit_balance += credit_amount
            user.save()
            request.session["credit_term"] = credit_term
            request.session["monthly_payment"] = float(monthly_payment)

            messages.success(request, f"Кредит оформлено на суму {credit_amount} грн на {credit_term} місяців.")
            return redirect("cards:add_credit", pk=pk)

        # Погашение кредита
        elif "repay_credit" in request.POST:
            if user.credit_balance > 0:
                user.credit_balance = Decimal(0)  # Обнуляем кредит
                user.save()

                # Очищаем данные о кредите
                request.session["credit_term"] = 0
                request.session["monthly_payment"] = None

                messages.success(request, "Ваш кредит успішно погашений!")
            else:
                messages.error(request, "У вас немає активного кредиту.")

            return redirect("cards:add_credit", pk=pk)

    return render(request, "cards/credit_plus.html", {
        "card": card,
        "user": user,
        "monthly_payment": monthly_payment,
        "credit_term": credit_term
    })

@login_required
def credit_info(request, pk):
    card = get_object_or_404(BankCard, pk=pk, user=request.user)
    user = card.user  # Получаем пользователя, связанного с картой

    # Получаем данные о кредите из сессии
    credit_term = request.session.get("credit_term", 0)
    monthly_payment = request.session.get("monthly_payment", None)

    if request.method == "POST":
        # Если нажата кнопка для погашения кредита
        if "repay_credit" in request.POST:
            if user.credit_balance > 0:
                user.credit_balance = 0  # Обнуляем кредит
                user.save()

                # Очищаем данные о кредите в сессии
                request.session["credit_term"] = 0
                request.session["monthly_payment"] = None

                messages.success(request, "Ваш кредит успішно погашений!")

            else:
                messages.error(request, "У вас немає активного кредиту.")

            return redirect("cards:credit_info", pk=pk)

    return render(request, "cards/credit_close.html", {
        "card": card,
        "user": user,
        "monthly_payment": monthly_payment,
        "credit_term": credit_term
    })