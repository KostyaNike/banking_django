from django.contrib import admin
from .models import Card, Account

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_number', 'expiration_date')


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'linked_card')