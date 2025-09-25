from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from mailing.models import Client, Mailing

User = get_user_model()


class Command(BaseCommand):
    help = "Setup user groups and permissions for admin panel"

    def handle(self, *args, **options):
        # Группа менеджеров
        manager_group, created = Group.objects.get_or_create(name="Managers")

        # Получаем разрешения
        content_type_client = ContentType.objects.get_for_model(Client)
        content_type_mailing = ContentType.objects.get_for_model(Mailing)
        content_type_user = ContentType.objects.get_for_model(User)

        # Права для менеджеров
        manager_permissions = []

        # Добавляем разрешения, если они существуют
        try:
            manager_permissions.append(
                Permission.objects.get(
                    codename="view_all_clients", content_type=content_type_client
                )
            )
        except Permission.DoesNotExist:
            pass

        try:
            manager_permissions.append(
                Permission.objects.get(
                    codename="view_all_mailings", content_type=content_type_mailing
                )
            )
        except Permission.DoesNotExist:
            pass

        try:
            manager_permissions.append(
                Permission.objects.get(
                    codename="view_user", content_type=content_type_user
                )
            )
            manager_permissions.append(
                Permission.objects.get(
                    codename="change_user", content_type=content_type_user
                )
            )
        except Permission.DoesNotExist:
            pass

        if manager_permissions:
            manager_group.permissions.set(manager_permissions)

        self.stdout.write(self.style.SUCCESS("Группы и права настроены успешно"))
