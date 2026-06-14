from django.contrib import admin
from .models import WasteCategory, PickupOrder, OrderStatusLog


class OrderStatusLogInline(admin.TabularInline):
    model = OrderStatusLog
    extra = 0
    readonly_fields = ('from_status', 'to_status', 'changed_by', 'timestamp', 'notes')
    can_delete = False


@admin.register(WasteCategory)
class WasteCategoryAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'base_price_kobo', 'price_per_kg_kobo', 'is_active')
    list_filter = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(PickupOrder)
class PickupOrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'customer', 'category', 'collector',
        'status', 'weight_kg', 'rating', 'created_at'
    )
    list_filter = ('status', 'category', 'is_immediate', 'created_at')
    search_fields = ('order_number', 'customer__phone', 'customer__name', 'address')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'assigned_at', 'completed_at')
    raw_id_fields = ('customer', 'collector')
    inlines = [OrderStatusLogInline]
    list_per_page = 30

    fieldsets = (
        ('Order Info', {'fields': ('order_number', 'customer', 'category', 'status')}),
        ('Location', {'fields': ('address', 'latitude', 'longitude')}),
        ('Scheduling', {'fields': ('is_immediate', 'scheduled_time')}),
        ('Collection', {'fields': ('collector', 'special_instructions', 'weight_kg')}),
        ('Photos', {'fields': ('arrival_photo', 'completion_photo')}),
        ('Feedback', {'fields': ('rating', 'rating_comment')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'assigned_at', 'completed_at')}),
    )


@admin.register(OrderStatusLog)
class OrderStatusLogAdmin(admin.ModelAdmin):
    list_display = ('order', 'from_status', 'to_status', 'changed_by', 'timestamp')
    list_filter = ('to_status',)
    search_fields = ('order__order_number',)
    readonly_fields = ('order', 'from_status', 'to_status', 'changed_by', 'timestamp')
