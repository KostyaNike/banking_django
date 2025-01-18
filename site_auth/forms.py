from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()  # Убедитесь, что email правильно обрабатывается

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ("email",)  # Добавление email

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        # Проверка пользователя по email
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise forms.ValidationError("Пользователь с таким email не найден.")

        # Проверка пароля
        if not user.check_password(password):
            raise forms.ValidationError("Неверный пароль.")

        self.cleaned_data['user'] = user
        return self.cleaned_data

class VerificationForm(forms.Form):
    code = forms.CharField(max_length=6)