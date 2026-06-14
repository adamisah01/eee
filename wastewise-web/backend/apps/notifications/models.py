"""
Notification log model for WasteWise.
Tracks all outbound notifications (SMS, push, WhatsApp).
"""
import uuid
from django.conf import settings
from django.db import models


class NotificationLog(models.Model):
    """Log of all notifications sent to users."""

    class Channel(models.TextChoices):
        SMS = 'sms', 'SMS'
        PUSH = 'push', 'Push Notification'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        EMAIL = 'email', 'Email'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SENT = 'sent', 'Sent'
        DELIVERED = 'delivered', 'Delivered'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications', null=True, blank=True
    )
    phone = models.CharField(max_length=15, blank=True, help_text='Recipient phone if no user')
    channel = models.CharField(max_length=20, choices=Channel.choices)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    external_id = models.CharField(max_length=200, blank=True, help_text='ID from SMS/push provider')
    metadata = models.JSONField(default=dict, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.channel} to {self.user or self.phone}: {self.subject or self.message[:50]}'
