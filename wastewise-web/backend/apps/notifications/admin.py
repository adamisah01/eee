from django.contrib import admin
from .models import NotificationLog


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('channel', 'user', 'phone', 'subject', 'status', 'sent_at', 'created_at')
    list_filter = ('channel', 'status', 'created_at')
    search_fields = ('phone', 'user__phone', 'message')
    readonly_fields = ('created_at', 'sent_at')
