from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from mailing.models import Mailing, MailingAttempt


class Command(BaseCommand):
    help = "Отправить запланированную рассылку"

    def handle(self, *args, **options):
        now = timezone.now()

        # Находим активные рассылки
        mailings = Mailing.objects.filter(
            status="started", start_time__lte=now, end_time__gte=now
        )

        for mailing in mailings:
            self.send_mailing(mailing)

    def send_mailing(self, mailing):
        for client in mailing.clients.all():
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[client.email],
                    fail_silently=False,
                )

                # Записываем успешную попытку
                MailingAttempt.objects.create(
                    mailing=mailing,
                    client=client,
                    status="успех",
                    server_response="Письмо успешно отправлено",
                )

            except Exception as e:
                # Записываем неудачную попытку
                MailingAttempt.objects.create(
                    mailing=mailing,
                    client=client,
                    status="неуспешный",
                    server_response=str(e),
                )
