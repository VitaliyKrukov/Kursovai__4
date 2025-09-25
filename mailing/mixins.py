from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class OwnerRequiredMixin(LoginRequiredMixin):
    """Миксин для проверки владельца объекта"""

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm(
            "mailing.view_all_clients"
        ) or self.request.user.has_perm("mailing.view_all_mailings"):
            return qs  # Менеджер видит все
        return qs.filter(owner=self.request.user)  # Пользователь видит только свои


class ManagerRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки прав менеджера"""

    def test_func(self):
        return self.request.user.has_perm(
            "mailing.view_all_clients"
        ) or self.request.user.has_perm("mailing.view_all_mailings")

    def handle_no_permission(self):
        from django.contrib import messages

        messages.error(self.request, "У вас нет прав для выполнения этого действия.")
        from django.shortcuts import redirect

        return redirect("mailing:index")


class OwnerOrManagerMixin(LoginRequiredMixin):
    """Миксин для владельца или менеджера"""

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if (
            obj.owner == self.request.user
            or self.request.user.has_perm("mailing.view_all_clients")
            or self.request.user.has_perm("mailing.view_all_mailings")
        ):
            return obj

        raise PermissionDenied("У вас нет прав для доступа к этому объекту.")
