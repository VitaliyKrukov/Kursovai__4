from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from .forms import ClientForm, MailingForm, MessageForm
from .mixins import ManagerRequiredMixin, OwnerOrManagerMixin, OwnerRequiredMixin
from .models import Client, Mailing, MailingAttempt, Message
from .services import send_mailing

User = get_user_model()


def index(request):
    total_mailings = Mailing.objects.count()
    active_mailings = Mailing.objects.filter(
        status="started", start_time__lte=timezone.now(), end_time__gte=timezone.now()
    ).count()
    unique_clients = Client.objects.values("email").distinct().count()

    context = {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "unique_clients": unique_clients,
    }
    return render(request, "mailing/index.html", context)


# ===== CLIENT VIEWS =====
class ClientListView(OwnerRequiredMixin, ListView):
    model = Client
    template_name = "mailing/client_list.html"


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(OwnerOrManagerMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client_list")


class ClientDeleteView(OwnerOrManagerMixin, DeleteView):
    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("mailing:client_list")


# ===== MESSAGE VIEWS =====
class MessageListView(OwnerRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(OwnerOrManagerMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageDeleteView(OwnerOrManagerMixin, DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")


# ===== MAILING VIEWS =====
class MailingListView(OwnerRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"


class MailingDetailView(OwnerOrManagerMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attempts"] = MailingAttempt.objects.filter(mailing=self.object)
        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Ограничиваем выбор только своими клиентами и сообщениями
        if not self.request.user.has_perm("mailing.view_all_clients"):
            form.fields["clients"].queryset = Client.objects.filter(
                owner=self.request.user
            )
            form.fields["message"].queryset = Message.objects.filter(
                owner=self.request.user
            )
        return form


class MailingUpdateView(OwnerOrManagerMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Для менеджера показываем все, для пользователя - только свои
        if not self.request.user.has_perm("mailing.view_all_clients"):
            form.fields["clients"].queryset = Client.objects.filter(
                owner=self.request.user
            )
            form.fields["message"].queryset = Message.objects.filter(
                owner=self.request.user
            )
        return form


class MailingDeleteView(OwnerOrManagerMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")


# ===== MAILING SEND VIEW =====
class MailingSendView(LoginRequiredMixin, View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        # Проверяем права: владелец или менеджер
        if request.user != mailing.owner and not request.user.has_perm(
            "mailing.view_all_mailings"
        ):
            messages.error(request, "У вас нет прав для отправки этой рассылки")
            return redirect("mailing:mailing_list")

        try:
            result = send_mailing(mailing)
            if result["success"] > 0:
                messages.success(
                    request,
                    f"Рассылка отправлена! Успешно: {result['success']}/{result['total']}",
                )
            else:
                messages.error(
                    request, f"Ошибка отправки: {', '.join(result['errors'])}"
                )
        except Exception as e:
            messages.error(request, f"Ошибка при отправке: {str(e)}")

        return redirect("mailing:mailing_detail", pk=mailing.pk)


# ===== ATTEMPT VIEWS =====
class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = "mailing/mailing_attempt_list.html"
    context_object_name = "attempts"

    def get_queryset(self):
        mailing_id = self.kwargs.get("pk")
        mailing = get_object_or_404(Mailing, pk=mailing_id)

        # Проверяем права доступа: владелец или менеджер
        if self.request.user != mailing.owner and not self.request.user.has_perm(
            "mailing.view_all_mailings"
        ):
            return MailingAttempt.objects.none()

        return MailingAttempt.objects.filter(mailing=mailing).select_related("client")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing_id = self.kwargs.get("pk")
        context["mailing"] = get_object_or_404(Mailing, pk=mailing_id)
        return context


# ===== STATISTICS VIEW =====
class StatisticsView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.has_perm("mailing.view_all_mailings"):
            # Статистика для менеджера
            mailings = Mailing.objects.all()
            clients = Client.objects.all()
            attempts = MailingAttempt.objects.all()
            users = User.objects.filter(is_staff=False)
        else:
            # Статистика для пользователя
            mailings = Mailing.objects.filter(owner=request.user)
            clients = Client.objects.filter(owner=request.user)
            attempts = MailingAttempt.objects.filter(mailing__owner=request.user)
            users = User.objects.none()

        context = {
            "total_mailings": mailings.count(),
            "active_mailings": mailings.filter(status="started").count(),
            "completed_mailings": mailings.filter(status="completed").count(),
            "total_clients": clients.count(),
            "successful_attempts": attempts.filter(status="success").count(),
            "failed_attempts": attempts.filter(status="failed").count(),
            "total_users": (
                users.count()
                if request.user.has_perm("mailing.view_all_mailings")
                else 0
            ),
        }
        return render(request, "mailing/statistics.html", context)


# ===== MANAGER VIEWS =====
class ManagerMailingListView(ManagerRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/manager_mailing_list.html"
    context_object_name = "mailings"


class ManagerClientListView(ManagerRequiredMixin, ListView):
    model = Client
    template_name = "mailing/manager_client_list.html"
    context_object_name = "clients"


class ManagerUserListView(ManagerRequiredMixin, ListView):
    model = User
    template_name = "mailing/manager_user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        return User.objects.filter(is_staff=False)


# ===== MANAGER ACTIONS =====
class MailingDisableView(ManagerRequiredMixin, View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.status = "completed"
        mailing.save()
        messages.success(request, f"Рассылка #{mailing.id} отключена")
        return redirect("mailing:manager_mailing_list")


class UserBlockView(ManagerRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        action = "разблокирован" if user.is_active else "заблокирован"
        messages.success(request, f"Пользователь {user.username} {action}")
        return redirect("mailing:manager_user_list")
