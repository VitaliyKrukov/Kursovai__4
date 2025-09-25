from django.core.management.base import BaseCommand
from django.utils import timezone

from mailing.models import Mailing
from mailing.services import send_mailing


class Command(BaseCommand):
    help = "Отправляет рассылки по требованию или по расписанию"

    def add_arguments(self, parser):
        parser.add_argument(
            "--mailing-id",
            type=int,
            help="ID конкретной рассылки для отправки",
        )
        parser.add_argument(
            "--all-active",
            action="store_true",
            help="Отправить все активные рассылки",
        )

    def handle(self, *args, **options):
        mailing_id = options.get("mailing_id")
        send_all_active = options.get("all_active")

        if mailing_id:
            # Отправка конкретной рассылки
            try:
                mailing = Mailing.objects.get(pk=mailing_id)
                self.stdout.write(
                    f"Отправка рассылки #{mailing_id}: {mailing.message.subject}"
                )

                result = send_mailing(mailing)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Рассылка #{mailing_id} отправлена. "
                        f"Успешно: {result['success']}/{result['total']}"
                    )
                )

                if result["errors"]:
                    self.stdout.write(
                        self.style.WARNING(f"Ошибки: {', '.join(result['errors'])}")
                    )

            except Mailing.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(f"Рассылка #{mailing_id} не найдена")
                )

        elif send_all_active:
            # Отправка всех активных рассылок
            active_mailings = Mailing.objects.filter(
                status="started",
                start_time__lte=timezone.now(),
                end_time__gte=timezone.now(),
            )

            total_sent = 0
            for mailing in active_mailings:
                self.stdout.write(
                    f"Отправка рассылки #{mailing.pk}: {mailing.message.subject}"
                )
                result = send_mailing(mailing)
                total_sent += 1

                self.stdout.write(
                    f"Рассылка #{mailing.pk}: {result['success']}/{result['total']} успешно"
                )

                if result["errors"]:
                    self.stdout.write(
                        self.style.WARNING(f"Ошибки: {', '.join(result['errors'])}")
                    )

            self.stdout.write(
                self.style.SUCCESS(f"Всего отправлено рассылок: {total_sent}")
            )

        else:
            self.stderr.write(
                self.style.ERROR(
                    "Укажите --mailing-id ID или --all-active для отправки всех активных рассылок"
                )
            )
