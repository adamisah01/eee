from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPVerification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('phone', 'name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('phone', 'name', 'email')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal Info', {'fields': ('name', 'email', 'address', 'lga')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('phone', 'code', 'is_used', 'created_at', 'expires_at')
    list_filter = ('is_used',)
    search_fields = ('phone',)
    readonly_fields = ('code', 'created_at')
