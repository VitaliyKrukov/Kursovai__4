import logging
import smtplib

from django.conf import settings
from django.core.mail import BadHeaderError, send_mail
from django.utils import timezone

from .models import MailingAttempt

logger = logging.getLogger(__name__)


def send_single_email(mailing, client):
    """Отправляет одно письмо одному клиенту и возвращает результат"""
    try:
        # Отправляем email через Django
        send_mail(
            subject=mailing.message.subject,
            message=mailing.message.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client.email],
            fail_silently=False,
        )

        return {"status": "success", "response": "Сообщение успешно доставлено"}

    except BadHeaderError:
        error_msg = "Invalid header found"
        logger.error(f"Invalid header for {client.email}")
        return {"status": "failed", "response": error_msg}

    except smtplib.SMTPAuthenticationError:
        error_msg = "Authentication failed. Check email settings."
        logger.error(f"SMTP Authentication failed for {client.email}")
        return {"status": "failed", "response": error_msg}

    except smtplib.SMTPRecipientsRefused:
        error_msg = "Recipient email refused"
        logger.error(f"Recipient refused: {client.email}")
        return {"status": "failed", "response": error_msg}

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error sending to {client.email}: {error_msg}")
        return {"status": "failed", "response": error_msg}


def send_mailing(mailing):
    """
    Основная функция отправки рассылки с улучшенной обработкой ошибок
    """
    if not mailing.clients.exists():
        MailingAttempt.objects.create(
            mailing=mailing,
            status="failed",
            server_response="Нет получателей для рассылки",
            client=None,
        )
        return {"success": 0, "total": 0, "errors": ["Нет получателей для рассылки"]}

    if mailing.status == "completed":
        MailingAttempt.objects.create(
            mailing=mailing,
            status="failed",
            server_response="Рассылка уже завершена",
            client=None,
        )
        return {"success": 0, "total": 0, "errors": ["Рассылка уже завершена"]}

    # Проверяем настройки email
    if not all([settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD]):
        MailingAttempt.objects.create(
            mailing=mailing,
            status="failed",
            server_response="Email настройки не сконфигурированы",
            client=None,
        )
        return {
            "success": 0,
            "total": 0,
            "errors": ["Email настройки не сконфигурированы"],
        }

    # Обновляем статус рассылки
    if mailing.status != "started":
        mailing.status = "started"
        mailing.save()

    success_count = 0
    errors = []
    clients = mailing.clients.all()
    total = clients.count()

    # Общая запись о начале рассылки
    mailing_attempt = MailingAttempt.objects.create(
        mailing=mailing,
        status="processing",
        server_response=f"Начало рассылки для {total} получателей",
        client=None,
    )

    for client in clients:
        result = send_single_email(mailing, client)

        if result["status"] == "success":
            success_count += 1
        else:
            errors.append(f"{client.email}: {result['response']}")

    # Обновляем общую запись
    mailing_attempt.status = "success" if success_count > 0 else "failed"
    mailing_attempt.server_response = f"Завершено: {success_count}/{total} успешно"
    mailing_attempt.save()

    # Обновляем статус рассылки
    if mailing.end_time and mailing.end_time <= timezone.now():
        mailing.status = "completed"
    elif success_count > 0:
        mailing.status = "started"
    else:
        mailing.status = "created"
    mailing.save()

    return {"success": success_count, "total": total, "errors": errors}
