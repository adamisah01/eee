"""
Custom User model and OTP verification for WasteWise.
Phone number is the primary authentication identifier.
"""
import uuid
import random
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from datetime import timedelta
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model using phone number as the unique identifier."""

    class Role(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        COLLECTOR = 'collector', 'Collector'
        ADMIN = 'admin', 'Admin'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=15, unique=True, db_index=True)
    name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CUSTOMER)
    address = models.TextField(blank=True)
    lga = models.CharField(max_length=100, blank=True, help_text='Local Government Area')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.name or "User"} ({self.phone})'


class OTPVerification(models.Model):
    """One-time password for phone authentication. Expires in 5 minutes."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=15, db_index=True)
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'otp_verifications'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(
                minutes=getattr(settings, 'OTP_EXPIRY_MINUTES', 5)
            )
        if not self.code:
            self.code = f'{random.randint(0, 999999):06d}'
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def __str__(self):
        return f'OTP {self.code} for {self.phone}'
