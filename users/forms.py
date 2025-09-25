from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ["email", "username", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email


class ProfileForm(UserChangeForm):
    password = None  # Убираем поле пароля

    class Meta:
        model = User
        fields = ["username", "email", "phone", "country", "avatar"]
        widgets = {
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }
