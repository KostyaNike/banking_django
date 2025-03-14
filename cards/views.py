from django.shortcuts import render, get_object_or_404, redirect
from site_auth.models import BankCard, CustomUser
from money_trans.models import Transaction
from django.contrib import messages
from decimal import Decimal, InvalidOperation  # Подключаем модель транзакций
import feedparser
from .gtfs_processor import get_routes
import re
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Banka, UserCashback
from .forms import BankaForm, BankTransferForm, BankAccountForm
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Sum
from django.core.exceptions import ValidationError

def cards(request):
    if not request.user.is_authenticated:
        return render(request, "cards/cards.html")  # Вернем страницу с сообщением

    # Если пользователь авторизован, получаем его карты
    cards = BankCard.objects.filter(user=request.user)
    context = {
        "cards": cards
    }
    return render(request, "cards/cards.html", context)

from decimal import Decimal, ROUND_DOWN

def card(request, pk):
    if not request.user.is_authenticated:
        return render(request, "cards/card.html")
    # Получение конкретной карты пользователя
    card = get_object_or_404(BankCard, pk=pk, user=request.user)
    transactions = Transaction.objects.filter(card=card).order_by("-date")

    total_amount = transactions.aggregate(total=Sum('amount'))['total'] or Decimal(0)
    total_amount = total_amount.quantize(Decimal('0.01'), rounding=ROUND_DOWN)  # Округление до 2 знаков

    total_count = Decimal(transactions.count()).quantize(Decimal('0.01'), rounding=ROUND_DOWN)  # Округление до 2 знаков

    context = {
        "card": card,
        "transactions": transactions,
        "total_amount": total_amount,
        "total_count": total_count,  # Теперь округлено до 2 знаков
    }
    return render(request, "cards/card.html", context)
    

def mobile_service(request, pk):
    if not request.user.is_authenticated:
        return render(request, "cards/mobile.html")
    
    card = get_object_or_404(BankCard, pk=pk, user=request.user)
    user_cashback = get_object_or_404(UserCashback, user=request.user)
    
    if request.method == 'POST':
        phone_number = request.POST['phone_number']
        amount = Decimal(request.POST['amount'])
        
        # Проверка, достаточно ли средств на карте
        if amount <= card.balance:
            # Рассчитываем 2% от суммы пополнения
            cashback_amount = amount * Decimal(0.02)
            
            # Проверяем, не превышает ли сумма кешбека максимальный лимит
            if user_cashback.get_total_cashback() + cashback_amount <= 5160:
                # Добавляем кешбек в категорию "Поповнення мобільного"
                user_cashback.mobile_recharge += cashback_amount
                user_cashback.save()
                
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
                messages.success(request, f'Поповнення успішне! Ви поповнили мобільний на {amount} грн. Ваш кешбек: {round(cashback_amount, 2)} грн.')
            else:
                # Если кешбек превысит лимит, уведомляем пользователя
                messages.warning(request, 'Максимальний ліміт кешбеку досягнуто. Поповнення не здійснено.')
        else:
            messages.error(request, 'Недостатньо коштів для поповнення.')
    
    return render(request, 'cards/mobile.html', {'card': card})

def transfer(request, pk):
    if not request.user.is_authenticated:
        return render(request, "cards/transfer.html")
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
                messages.success(request, 'Успішний переказ!')
            else:
                messages.error(request, 'Недостатньо коштів для переказу.')
        else:
            messages.error(request, 'Не можна переказати гроші самому собі.')
    return render(request, 'cards/transfer.html', {'card': card})

def delete_card(request, pk):
    if not request.user.is_authenticated:
        return render(request, "cards/close_card.html")
    card = get_object_or_404(BankCard, pk=pk, user=request.user)
    if request.method == 'POST':
        card.delete()
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
    if not request.user.is_authenticated:
        return render(request, "cards/train.html")
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
    if not request.user.is_authenticated:
        return render(request, "cards/auto_parking.html")
    
    card = get_object_or_404(BankCard, pk=pk, user=request.user)
    user_cashback = get_object_or_404(UserCashback, user=request.user)

    if request.method == 'POST':
        city = request.POST.get('city')
        car_number = request.POST.get('car_number')

        # Регулярное выражение для украинского номера
        car_number_pattern = r'^[A-Z]{2}[0-9]{4}[A-Z]{2}$'

        # Проверка формата номера
        if not re.match(car_number_pattern, car_number):
            error_message = 'Номер автомобіля має бути у форматі XX0000XX (например, AB1234CD).'
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

                # Рассчитываем 2% кешбека от стоимости парковки
                cashback_amount = parking_fee * Decimal(0.02)

                # Проверяем, не превышает ли сумма кешбека максимальный лимит
                if user_cashback.get_total_cashback() + cashback_amount <= 5160:
                    # Добавляем кешбек в категорию "Парковка"
                    user_cashback.parking += cashback_amount
                    user_cashback.save()

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

                    # Сообщение об успешной оплате и кешбеке
                    messages.success(request, f'Оплата пройшла успішно! Ви оплатили парковку на {parking_fee} грн. Ваш кешбек: {round(cashback_amount, 2)} грн.')
                    messages.success(request, f'Ви успішно придбали абонемент на парковку, ваш кешбек: {round(cashback_amount, 2)} грн.')

                else:
                    # Если кешбек превысит лимит, уведомляем пользователя
                    messages.warning(request, 'Максимальний ліміт кешбеку досягнуто. Парковка не була оплачена.')
                
                return render(request, 'cards/auto_parking.html', {'card': card})

            except Exception as e:
                error_message = f'Помилка транзакції: {str(e)}'
                return render(request, 'cards/auto_parking.html', {'card': card, 'error_message': error_message})

        else:
            error_message = 'Недостатньо коштів на карті.'
            return render(request, 'cards/auto_parking.html', {'card': card, 'error_message': error_message})

    return render(request, 'cards/auto_parking.html', {'card': card})

def check_auto_fines(request, pk):
    if not request.user.is_authenticated:
        return render(request, "cards/auto_fine_parking.html")
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
    if not request.user.is_authenticated:
        return render(request, "cards/auto_pdr.html")
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
    if not request.user.is_authenticated:
        return render(request, "cards/credit_plus.html")
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

            return redirect("cards:add_credit", pk=pk)

    return render(request, "cards/credit_plus.html", {
        "card": card,
        "user": user,
        "monthly_payment": monthly_payment,
        "credit_term": credit_term
    })

@login_required
def credit_info(request, pk):
    if not request.user.is_authenticated:
        return render(request, "cards/credit_close.html")
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

            return redirect("cards:credit_info", pk=pk)

    return render(request, "cards/credit_close.html", {
        "card": card,
        "user": user,
        "monthly_payment": monthly_payment,
        "credit_term": credit_term
    })

@login_required
def insurance_health(request, pk):
    if not request.user.is_authenticated:
        return render(request, "cards/insurance_health.html")
    """Сторінка оформлення страхування здоров'я."""
    card = get_object_or_404(BankCard, pk=pk, user=request.user)
    insurance_price = Decimal(600)  # Стоимость страховки

    if request.method == "POST":
        if card.balance >= insurance_price:
            # Списываем деньги
            card.balance -= insurance_price
            card.save()
            messages.success(request, "Страховка здоров'я успішно оформлена!")
        else:
            messages.error(request, "Недостатньо коштів на карті!")

    return render(request, "cards/insurance_health.html", {
        "card": card,
        "insurance_price": insurance_price,
    })


@login_required
def insurance_touristic(request, pk):
    if not request.user.is_authenticated:
        return render(request, "cards/insurance_touristic.html")
    """Сторінка оформлення туристичної страховки."""
    card = get_object_or_404(BankCard, pk=pk, user=request.user)
    insurance_price = Decimal(600)  # Стоимость страховки

    if request.method == "POST":
        if card.balance >= insurance_price:
            # Списываем деньги
            card.balance -= insurance_price
            card.save()
            messages.success(request, "Туристична страховка успішно оформлена!")
        else:
            messages.error(request, "Недостатньо коштів на карті!")

    return render(request, "cards/insurance_touristic.html", {
        "card": card,
        "insurance_price": insurance_price,
    })

def open_banka(request, pk):
    if not request.user.is_authenticated:
        return render(request, "cards/banka_open.html")
    card = get_object_or_404(BankCard, pk=pk, user=request.user)

    if request.method == 'POST':
        form = BankaForm(request.POST)
        if form.is_valid():
            banka = form.save(commit=False)
            banka.user = request.user
            banka.save()
        return redirect('cards:cards')
    else:
        form = BankaForm()

    return render(request, 'cards/banka_open.html', {'form': form})

def banka_detail(request, pk):
    if not request.user.is_authenticated:
        return render(request, "cards/banka_my.html")
    card = get_object_or_404(BankCard, pk=pk, user=request.user)
    try:
        banka = request.user.banka  # Получаем банку, привязанную к текущему пользователю
    except Banka.DoesNotExist:
        banka = None

    return render(request, 'cards/banka_my.html', {'banka': banka})

@login_required
def bank_transfer(request, pk):
    if not request.user.is_authenticated:
        return render(request, "cards/banka_send.html")
    # Получаем карточку пользователя и его накопительную банку
    user_card = get_object_or_404(BankCard, pk=pk, user=request.user)
    user_banka = Banka.objects.filter(user=request.user).first()  # Получаем банку пользователя, если она есть

    if request.method == 'POST':
        form = BankTransferForm(request.POST)
        if form.is_valid():
            transfer_type = form.cleaned_data['transfer_type']
            amount = form.cleaned_data['amount']
            hash_code = form.cleaned_data['hash_code'] if transfer_type == 'other' else None

            # Проверка, хватает ли средств на основном балансе
            if user_card.balance < amount:
                messages.error(request, "Недостатньо коштів на основному рахунку.")
                return render(request, 'cards/banka_send.html', {'form': form, 'user_banka': user_banka})

            # Пополнение своей банки
            if transfer_type == 'self':
                if user_banka:
                    user_banka.balance += amount
                    user_banka.save()
                    user_card.balance -= amount  # Снимаем деньги с основного баланса
                    user_card.save()
                    messages.success(request, f"Вашу банку поповнено на {amount} грн.")

            # Отправка на чужую банку
            elif transfer_type == 'other':
                # Проверка на наличие хеш-кода для отправки на чужую банку
                if not hash_code:
                    messages.error(request, "Будь ласка, введіть хеш-код чужої банки.")
                    return render(request, 'cards/banka_send.html', {'form': form, 'user_banka': user_banka})

                # Проверяем наличие чужой банки по хеш-коду
                try:
                    other_banka = Banka.objects.get(hash_code=hash_code)
                    other_banka.balance += amount
                    user_card.balance -= amount  # Снимаем деньги с основного баланса
                    user_card.save()
                    other_banka.save()
                    messages.success(request, f"Ви відправили {amount} грн на чужу банку.")
                except Banka.DoesNotExist:
                    messages.error(request, "Банку з таким хеш-кодом не знайдено.")

            return render(request, 'cards/banka_send.html', {'form': form, 'user_banka': user_banka})

    else:
        form = BankTransferForm()

    return render(request, 'cards/banka_send.html', {'form': form, 'user_banka': user_banka})

def close_banka(request, pk):
    if not request.user.is_authenticated:
        return render(request, "cards/card.html")
    message = None
    banka = Banka.objects.get(id=pk)
    banka.delete()  # Удаляем накопительную банку
    return redirect('cards:cards')

def add_balance(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")  # Если пользователь не авторизован, перенаправляем на страницу входа

    # Получаем карту по pk
    card = get_object_or_404(BankCard, pk=pk, user=request.user)

    if request.method == 'POST':
        try:
            # Получаем номер карты PayPal и сумму пополнения из формы
            paypal_card_number = request.POST.get('paypal_card_number', '').strip()
            amount = Decimal(request.POST['amount'])

            # Проверка, что номер карты содержит 16 символов
            if len(paypal_card_number) != 16 or not paypal_card_number.isdigit():
                raise ValidationError("Номер картки PayPal має містити 16 цифр.")

            if amount <= 0:
                raise ValueError("Сума має бути правильною.")

            # Пополнение баланса
            card.balance += amount
            card.save()

            # Создание транзакции
            # recipient - это текущий пользователь, так как он получает деньги
            transaction = Transaction.objects.create(
                card=card,
                recipient=request.user,  # recipient = текущий пользователь
                amount=amount,
                transaction_type="deposit"
            )

            messages.success(request, f"На рахунок картки {card.card_number} зачіслено {amount} грн.")

        except ValueError as e:
            messages.error(request, f"Помилка: {e}")
        except ValidationError as e:
            messages.error(request, f"Помилка: {e}")

    # Отправляем данные в шаблон
    return render(request, "cards/add_balance.html", {"card": card})

def cashback(request, pk):
    user = request.user  # Получаем текущего пользователя

    # Получаем кешбэк для пользователя или создаем новый, если его нет
    try:
        cashback_data = UserCashback.objects.get(user=user)
    except UserCashback.DoesNotExist:
        cashback_data = UserCashback.objects.create(user=user, max_cashback=5160)

    cashback_percentage = cashback_data.get_cashback_percentage()

    # Проверим, что данные выводятся
    print(cashback_data)  # Добавьте этот вывод для отладки

    return render(request, "cards/cashback.html", {
        "cashback_data": cashback_data,
        "cashback_percentage": cashback_percentage
    })

@login_required
def remove_cashback(request):
    if request.method == 'POST':
        user_cashback = UserCashback.objects.get(user=request.user)
        card = BankCard.objects.get(user=request.user)

        total_cashback = user_cashback.get_total_cashback()

        if total_cashback > 0:
            # Переводим кешбек на баланс карты
            card.balance += total_cashback
            card.save()

            # Обнуляем кешбек
            user_cashback.cafe_restaurants = 0
            user_cashback.kids_stores = 0
            user_cashback.e_scooters = 0
            user_cashback.cinemas = 0
            user_cashback.transport = 0
            user_cashback.mobile_recharge = 0
            user_cashback.parking = 0
            user_cashback.save()

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})

    return JsonResponse({'success': False})

def open_account(request):
    if request.method == 'POST':
        form = BankAccountForm(request.POST, request.FILES)
        if form.is_valid():
            # Обработка данных формы, например, сохранение в базу данных
            # Пример: save form data to model or redirect to confirmation page
            return redirect('success_page')  # Перенаправление на страницу успеха
    else:
        form = BankAccountForm()
    
    return render(request, 'cards/cards_open.html', {'form': form})