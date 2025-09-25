import hashlib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views.generic import CreateView, DetailView, UpdateView

from .forms import ProfileForm, RegisterForm
from .models import User


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.instance

        # Генерируем токен для подтверждения email
        token = get_random_string(50)
        user.token = hashlib.sha256(token.encode()).hexdigest()
        user.is_active = False  # Деактивируем до подтверждения
        user.save()

        # Отправляем email с подтверждением
        verification_url = self.request.build_absolute_uri(
            reverse_lazy("users:verify_email", kwargs={"token": token})
        )

        send_mail(
            subject="Подтверждение email адреса",
            message=f"Для подтверждения email перейдите по ссылке: {verification_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        messages.info(
            self.request,
            "На ваш email отправлено письмо с подтверждением. "
            "Пожалуйста, проверьте почту и перейдите по ссылке для активации аккаунта.",
        )
        return response


def verify_email(request, token):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    try:
        user = User.objects.get(token=token_hash, is_active=False)
        user.is_active = True
        user.token = None
        user.save()
        messages.success(
            request, "Email успешно подтвержден! Теперь вы можете войти в систему."
        )
        return redirect("users:login")
    except User.DoesNotExist:
        messages.error(request, "Неверная или устаревшая ссылка подтверждения.")
        return redirect("users:login")


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "users/profile.html"
    context_object_name = "user"

    def get_object(self):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Профиль успешно обновлен!")
        return super().form_valid(form)
