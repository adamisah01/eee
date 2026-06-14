"""
Collector models for WasteWise.
Covers collector profiles, availability, and location tracking.
"""
import uuid
from django.conf import settings
from django.db import models


class CollectorProfile(models.Model):
    """Extended profile for users with role='collector'."""

    class VehicleType(models.TextChoices):
        KEKE = 'keke', 'Keke (Tricycle)'
        TRUCK = 'truck', 'Truck'
        VAN = 'van', 'Van'
        MOTORCYCLE = 'motorcycle', 'Motorcycle'
        OTHER = 'other', 'Other'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='collector_profile'
    )
    is_online = models.BooleanField(default=False, db_index=True)
    is_verified = models.BooleanField(default=False)
    vehicle_type = models.CharField(
        max_length=20, choices=VehicleType.choices, default=VehicleType.KEKE
    )
    vehicle_plate = models.CharField(max_length=20, blank=True)
    service_areas = models.JSONField(
        default=list, blank=True,
        help_text='List of LGA names this collector serves'
    )
    id_document = models.ImageField(
        upload_to='documents/ids/', null=True, blank=True,
        help_text='Government ID for verification'
    )
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00,
        help_text='Average rating from customers (1.00 - 5.00)'
    )
    total_jobs = models.IntegerField(default=0)
    total_earnings_kobo = models.BigIntegerField(default=0)

    # Current location (last known)
    current_latitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    current_longitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    last_location_update = models.DateTimeField(null=True, blank=True)

    # Bank details for payouts
    bank_name = models.CharField(max_length=100, blank=True)
    bank_code = models.CharField(max_length=10, blank=True)
    account_number = models.CharField(max_length=20, blank=True)
    account_name = models.CharField(max_length=150, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'collector_profiles'

    def __str__(self):
        status = '🟢' if self.is_online else '⚫'
        return f'{status} {self.user.name} ({self.get_vehicle_type_display()})'


class CollectorLocationHistory(models.Model):
    """GPS location log for collectors during active jobs."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collector = models.ForeignKey(
        CollectorProfile, on_delete=models.CASCADE,
        related_name='location_history'
    )
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'collector_location_history'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['collector', '-timestamp']),
        ]

    def __str__(self):
        return f'{self.collector.user.name} @ ({self.latitude}, {self.longitude})'
