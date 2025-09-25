from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Тестирование настроек email"

    def handle(self, *args, **options):
        try:
            send_mail(
                subject="Тестовое письмо от Django рассылки",
                message="Это тестовое письмо для проверки настроек email.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.EMAIL_HOST_USER],  # Отправляем себе
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS("Тестовое письмо успешно отправлено!"))
            self.stdout.write(f"От: {settings.DEFAULT_FROM_EMAIL}")
            self.stdout.write(f"SMTP: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ошибка отправки: {e}"))
            self.stdout.write("Проверьте настройки в .env файле:")
            self.stdout.write(
                "1. EMAIL_HOST_USER - ваш email\n"
                "2. EMAIL_HOST_PASSWORD - пароль приложения (не пароль от email!)\n"
                "3. Для Gmail нужно включить двухфакторную auth и создать пароль приложения"
            )
