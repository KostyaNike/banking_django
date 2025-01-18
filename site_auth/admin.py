from django.contrib import admin
from .models import CustomUser, BankCard
from django.contrib.auth.admin import UserAdmin

admin.site.register(CustomUser)
admin.site.register(BankCard)

# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     model = CustomUser
#     list_display = ('username', 'email', 'is_active', 'is_staff')
#     fieldsets = UserAdmin.fieldsets + (
#         ('Verification', {'fields': ('verification_code',)}),
#     )

# @admin.register(BankCard)
# class BankCardAdmin(admin.ModelAdmin):
#     list_display = ('user', 'card_number', 'balance', 'expiry_date')
#     readonly_fields = ('card_number', 'cvv', 'expiry_date')