from django.contrib import admin
from .models import CollectorProfile, CollectorLocationHistory


@admin.register(CollectorProfile)
class CollectorProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'is_online', 'is_verified', 'vehicle_type',
        'rating', 'total_jobs', 'total_earnings_kobo'
    )
    list_filter = ('is_online', 'is_verified', 'vehicle_type')
    search_fields = ('user__phone', 'user__name', 'vehicle_plate')
    readonly_fields = ('total_jobs', 'total_earnings_kobo', 'rating', 'created_at', 'updated_at')
    raw_id_fields = ('user',)

    fieldsets = (
        ('Status', {'fields': ('user', 'is_online', 'is_verified')}),
        ('Vehicle', {'fields': ('vehicle_type', 'vehicle_plate')}),
        ('Service', {'fields': ('service_areas', 'id_document')}),
        ('Stats', {'fields': ('rating', 'total_jobs', 'total_earnings_kobo')}),
        ('Location', {'fields': ('current_latitude', 'current_longitude', 'last_location_update')}),
        ('Bank Details', {'fields': ('bank_name', 'bank_code', 'account_number', 'account_name')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(CollectorLocationHistory)
class CollectorLocationHistoryAdmin(admin.ModelAdmin):
    list_display = ('collector', 'latitude', 'longitude', 'timestamp')
    list_filter = ('timestamp',)
    raw_id_fields = ('collector',)
