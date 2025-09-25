from django.conf import settings
from django.db import models
from django.utils import timezone


class Client(models.Model):
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        null=True,
        blank=True,
    )
    full_name = models.CharField(
        max_length=255,
        verbose_name="ФИО",
        null=True,
        blank=True,
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Владелец",
    )

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    class Meta:
        verbose_name = "клиент"
        verbose_name_plural = "клиенты"
        permissions = [
            ("view_all_clients", "Can view all clients"),
        ]


class Message(models.Model):
    subject = models.CharField(
        max_length=255,
        verbose_name="Тема письма",
        null=True,
        blank=True,
    )
    body = models.TextField(
        verbose_name="Тело письма",
        null=True,
        blank=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Владелец",
    )

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "сообщение"
        verbose_name_plural = "сообщения"


class Mailing(models.Model):
    STATUS_CHOICES = [
        ("created", "Создана"),
        ("started", "Запущена"),
        ("completed", "Завершена"),
    ]

    start_time = models.DateTimeField(verbose_name="Время начала отправки")
    end_time = models.DateTimeField(verbose_name="Время окончания отправки")
    status = models.CharField(
        max_length=40, choices=STATUS_CHOICES, default="created", verbose_name="Статус"
    )
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, verbose_name="Сообщение"
    )
    clients = models.ManyToManyField(Client, verbose_name="Получатели")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Владелец",
    )

    def __str__(self):
        return f"Рассылка {self.id} - {self.get_status_display()}"

    def is_active(self):
        now = timezone.now()
        return self.status == "started" and self.start_time <= now <= self.end_time

    class Meta:
        verbose_name = "рассылка"
        verbose_name_plural = "рассылки"
        permissions = [
            ("view_all_mailings", "Can view all mailings"),
            ("disable_mailing", "Can disable mailing"),
        ]


class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ("success", "Успешно"),
        ("failed", "Не успешно"),
    ]

    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Время попытки")
    status = models.CharField(
        max_length=40,
        choices=STATUS_CHOICES,
        verbose_name="Статус",
        null=True,
        blank=True,
    )
    server_response = models.TextField(
        blank=True, null=True, verbose_name="Ответ сервера"
    )
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        verbose_name="Рассылка",
        null=True,
        blank=True,
    )
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, verbose_name="Клиент", null=True, blank=True
    )

    def __str__(self):
        return f"Попытка {self.id} - {self.get_status_display()}"

    class Meta:
        verbose_name = "попытка рассылки"
        verbose_name_plural = "попытки рассылок"
