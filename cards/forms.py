from django import forms
from .models import Banka
from decimal import Decimal
import datetime
from django.core.exceptions import ValidationError

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

class BankAccountForm(forms.Form):
    first_name = forms.CharField(label="Ім'я", max_length=100, required=True)
    last_name = forms.CharField(label="Прізвище", max_length=100, required=True)
    email = forms.EmailField(label="Email", required=True)
    phone_number = forms.CharField(label="Номер телефону", max_length=15, required=True)
    account_type = forms.ChoiceField(
        label="Тип рахунку",
        choices=[('personal', 'Особистий'), ('business', 'Для бізнесу')],
        required=True
    )
    birth_date = forms.DateField(
        label="Дата народження",
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    workplace = forms.CharField(label="Місце роботи", max_length=200, required=True)
    position = forms.CharField(label="Посада", max_length=100, required=True)
    monthly_income = forms.DecimalField(
        label="Середній дохід на місяць", max_digits=10, decimal_places=2, required=True
    )
    document = forms.FileField(
        label="Документ, що підтверджує дозвіл на кілька рахунків", required=True
    )
    comment = forms.CharField(
        label="Коментар", widget=forms.Textarea(attrs={'style': 'resize: none;'}), required=True
    )

    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        today = datetime.date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 18:
            raise ValidationError('Вік має бути більше 18 років.')
        return birth_date