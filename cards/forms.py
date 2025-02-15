from django import forms
from .models import Banka
from decimal import Decimal


class BankaForm(forms.ModelForm):
    class Meta:
        model = Banka
        fields = ['name', 'description', 'goal']  # Добавляем поле goal
        labels = {
            'name': 'Название банки',
            'description': 'Описание',
            'goal': 'Цель накопления (грн)',
        }

class BankTransferForm(forms.Form):
    TRANSFER_CHOICES = [
        ('self', 'На свою банку'),
        ('other', 'На чужую банку'),
    ]
    
    transfer_type = forms.ChoiceField(choices=TRANSFER_CHOICES, label="Тип перевода")
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label="Сумма")
    hash_code = forms.CharField(max_length=12, required=False, label="Хеш чужой банки")