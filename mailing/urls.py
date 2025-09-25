from django.urls import path

from . import views
from .views import (
    ClientCreateView,
    ClientDeleteView,
    ClientListView,
    ClientUpdateView,
    MailingCreateView,
    MailingDeleteView,
    MailingDetailView,
    MailingListView,
    MailingSendView,
    MailingUpdateView,
    MessageCreateView,
    MessageDeleteView,
    MessageListView,
    MessageUpdateView,
)

app_name = "mailing"

urlpatterns = [
    path("", views.index, name="index"),
    # Клиенты
    path("clients/", ClientListView.as_view(), name="client_list"),
    path("clients/create/", ClientCreateView.as_view(), name="client_create"),
    path("clients/<int:pk>/edit/", ClientUpdateView.as_view(), name="client_edit"),
    path("clients/<int:pk>/delete/", ClientDeleteView.as_view(), name="client_delete"),
    # Сообщения
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path("messages/<int:pk>/edit/", MessageUpdateView.as_view(), name="message_edit"),
    path(
        "messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"
    ),
    # Рассылки
    path("mailing/", MailingListView.as_view(), name="mailing_list"),
    path("mailing/create/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailing/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailing/<int:pk>/edit/", MailingUpdateView.as_view(), name="mailing_edit"),
    path(
        "mailing/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"
    ),
    path("mailing/<int:pk>/send/", MailingSendView.as_view(), name="mailing_send"),
    path(
        "mailing/<int:pk>/attempts/",
        views.MailingAttemptListView.as_view(),
        name="mailing_attempts",
    ),
    # Статистика
    path("statistics/", views.StatisticsView.as_view(), name="statistics"),
    # Менеджерские функции - просмотр всех данных
    path(
        "manager/mailings/",
        views.ManagerMailingListView.as_view(),
        name="manager_mailing_list",
    ),
    path(
        "manager/clients/",
        views.ManagerClientListView.as_view(),
        name="manager_client_list",
    ),
    path(
        "manager/users/", views.ManagerUserListView.as_view(), name="manager_user_list"
    ),
    # Менеджерские действия
    path(
        "manager/mailing/<int:pk>/disable/",
        views.MailingDisableView.as_view(),
        name="disable_mailing",
    ),
    path(
        "manager/user/<int:pk>/block/", views.UserBlockView.as_view(), name="block_user"
    ),
]
