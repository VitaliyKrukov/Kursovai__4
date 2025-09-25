from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from mailing.models import Client, Mailing

User = get_user_model()


class Command(BaseCommand):
    help = "Create user groups and permissions"

    def handle(self, *args, **options):
        # Группа менеджеров
        manager_group, created = Group.objects.get_or_create(name="Managers")

        # Права для менеджеров
        content_type_mailing = ContentType.objects.get_for_model(Mailing)
        content_type_client = ContentType.objects.get_for_model(Client)
        content_type_user = ContentType.objects.get_for_model(User)

        manager_permissions = [
            Permission.objects.get(
                codename="view_all_clients", content_type=content_type_client
            ),
            Permission.objects.get(
                codename="view_all_mailings", content_type=content_type_mailing
            ),
            Permission.objects.get(
                codename="disable_mailing", content_type=content_type_mailing
            ),
            Permission.objects.get(
                codename="view_user", content_type=content_type_user
            ),
            Permission.objects.get(
                codename="change_user", content_type=content_type_user
            ),
        ]

        manager_group.permissions.set(manager_permissions)

        self.stdout.write(self.style.SUCCESS("Группы и права созданы успешно"))
