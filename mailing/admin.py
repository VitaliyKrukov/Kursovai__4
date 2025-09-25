from django.contrib import admin

from .models import Client, Mailing, MailingAttempt, Message


class ClientAdmin(admin.ModelAdmin):
    list_display = ["email", "full_name", "owner", "comment"]
    list_filter = ["owner"]
    search_fields = ["email", "full_name"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.has_perm("mailing.view_all_clients"):
            return qs
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.owner_id:
            obj.owner = request.user
        super().save_model(request, obj, form, change)


class MessageAdmin(admin.ModelAdmin):
    list_display = ["subject", "owner"]
    list_filter = ["owner"]
    search_fields = ["subject", "body"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.has_perm("mailing.view_all_mailings"):
            return qs
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.owner_id:
            obj.owner = request.user
        super().save_model(request, obj, form, change)


class MailingAdmin(admin.ModelAdmin):
    list_display = ["id", "start_time", "end_time", "status", "owner"]
    list_filter = ["status", "owner", "start_time"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.has_perm("mailing.view_all_mailings"):
            return qs
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.owner_id:
            obj.owner = request.user
        super().save_model(request, obj, form, change)


class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ["mailing", "client", "attempt_time", "status"]
    list_filter = ["status", "attempt_time"]
    readonly_fields = ["attempt_time", "status", "server_response", "mailing", "client"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.has_perm("mailing.view_all_mailings"):
            return qs
        return qs.filter(mailing__owner=request.user)


# Регистрируем модели
admin.site.register(Client, ClientAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Mailing, MailingAdmin)
admin.site.register(MailingAttempt, MailingAttemptAdmin)
