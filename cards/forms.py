from django import forms
from .models import Banka

class BankaForm(forms.ModelForm):
    class Meta:
        model = Banka
        fields = ['name', 'description']