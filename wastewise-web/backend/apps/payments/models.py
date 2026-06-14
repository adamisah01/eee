"""
Payment models for WasteWise.
Covers invoices (pay-after), transactions, and collector payouts.
"""
import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta


class Invoice(models.Model):
    """
    Invoice generated after a collector completes a pickup.
    Customer has 24 hours to pay (pay-after model).
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        EXPIRED = 'expired', 'Expired (Unpaid after 24h)'
        REFUNDED = 'refunded', 'Refunded'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(
        'orders.PickupOrder', on_delete=models.CASCADE, related_name='invoice'
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices'
    )

    # Price breakdown (all amounts in kobo — 100 kobo = ₦1)
    base_amount_kobo = models.IntegerField(help_text='Base collection charge')
    weight_charge_kobo = models.IntegerField(default=0, help_text='Per-kg charge')
    platform_fee_kobo = models.IntegerField(default=5000, help_text='Platform fee (default ₦50)')
    total_amount_kobo = models.IntegerField(help_text='Total payable amount')

    # Paystack
    paystack_reference = models.CharField(max_length=100, unique=True, db_index=True)
    payment_url = models.URLField(blank=True, help_text='Paystack payment URL (fallback)')

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(help_text='24 hours from creation')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        if not self.total_amount_kobo:
            self.total_amount_kobo = (
                self.base_amount_kobo + self.weight_charge_kobo + self.platform_fee_kobo
            )
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return self.status == self.Status.PENDING and timezone.now() > self.expires_at

    @property
    def total_naira(self):
        return self.total_amount_kobo / 100

    def __str__(self):
        return f'Invoice {self.paystack_reference} — ₦{self.total_naira:.2f} ({self.status})'


class Transaction(models.Model):
    """Record of a Paystack payment attempt/completion."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name='transactions'
    )
    paystack_reference = models.CharField(max_length=100, db_index=True)
    amount_kobo = models.IntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f'Txn {self.paystack_reference} — {self.status}'


class CollectorPayout(models.Model):
    """Weekly payout to collectors via Paystack Transfer."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collector = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payouts'
    )
    amount_kobo = models.BigIntegerField()
    bank_code = models.CharField(max_length=10)
    account_number = models.CharField(max_length=20)
    transfer_code = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    period_start = models.DateField(help_text='Start of payout period')
    period_end = models.DateField(help_text='End of payout period')
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'collector_payouts'
        ordering = ['-created_at']

    @property
    def amount_naira(self):
        return self.amount_kobo / 100

    def __str__(self):
        return f'Payout ₦{self.amount_naira:.2f} to {self.collector.name} ({self.status})'
