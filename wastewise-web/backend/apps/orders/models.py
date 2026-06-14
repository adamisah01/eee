"""
Order models for WasteWise.
Covers waste categories, pickup orders, and status tracking.
"""
import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class WasteCategory(models.Model):
    """Types of waste that can be collected."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=10, default='🗑️', help_text='Emoji icon')
    description = models.TextField(blank=True)
    base_price_kobo = models.IntegerField(
        help_text='Base collection price in kobo (100 kobo = ₦1)'
    )
    price_per_kg_kobo = models.IntegerField(
        default=0,
        help_text='Additional charge per kg in kobo'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'waste_categories'
        verbose_name_plural = 'Waste Categories'
        ordering = ['name']

    def __str__(self):
        return f'{self.icon} {self.name}'


class PickupOrder(models.Model):
    """A single waste collection order placed by a customer."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ASSIGNED = 'assigned', 'Collector Assigned'
        EN_ROUTE = 'en_route', 'Collector En Route'
        ARRIVED = 'arrived', 'Collector Arrived'
        COLLECTING = 'collecting', 'Collecting Waste'
        COMPLETED = 'completed', 'Collection Completed'
        PAYMENT_PENDING = 'payment_pending', 'Payment Pending'
        PAID = 'paid', 'Paid'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(
        max_length=12, unique=True, db_index=True,
        help_text='Human-readable order ID, e.g. WW12345678'
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='orders'
    )
    category = models.ForeignKey(
        WasteCategory, on_delete=models.PROTECT, related_name='orders'
    )
    collector = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_orders'
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )

    # Location
    address = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # Scheduling
    scheduled_time = models.DateTimeField(
        null=True, blank=True,
        help_text='Null means "as soon as possible"'
    )
    is_immediate = models.BooleanField(default=True)

    # Details
    special_instructions = models.TextField(blank=True)
    weight_kg = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        help_text='Actual weight recorded by collector'
    )
    rating = models.IntegerField(
        null=True, blank=True,
        help_text='1-5 star rating from customer'
    )
    rating_comment = models.TextField(blank=True)

    # Photos
    arrival_photo = models.ImageField(upload_to='photos/arrivals/', null=True, blank=True)
    completion_photo = models.ImageField(upload_to='photos/completions/', null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'pickup_orders'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            self.order_number = f'WW{random.randint(10000000, 99999999)}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.order_number} — {self.get_status_display()}'


class OrderStatusLog(models.Model):
    """Audit log for every status change on an order."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        PickupOrder, on_delete=models.CASCADE, related_name='status_logs'
    )
    from_status = models.CharField(max_length=20, choices=PickupOrder.Status.choices)
    to_status = models.CharField(max_length=20, choices=PickupOrder.Status.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_status_logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.order.order_number}: {self.from_status} → {self.to_status}'
