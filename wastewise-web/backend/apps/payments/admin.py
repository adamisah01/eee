from django.contrib import admin
from .models import Invoice, Transaction, CollectorPayout


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    readonly_fields = ('paystack_reference', 'amount_kobo', 'status', 'created_at')
    can_delete = False


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'paystack_reference', 'order', 'customer',
        'total_amount_kobo', 'status', 'paid_at', 'expires_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('paystack_reference', 'order__order_number', 'customer__phone')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('order', 'customer')
    inlines = [TransactionInline]

    fieldsets = (
        ('Order', {'fields': ('order', 'customer')}),
        ('Pricing', {'fields': ('base_amount_kobo', 'weight_charge_kobo', 'platform_fee_kobo', 'total_amount_kobo')}),
        ('Paystack', {'fields': ('paystack_reference', 'payment_url')}),
        ('Status', {'fields': ('status', 'paid_at', 'expires_at')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('paystack_reference', 'invoice', 'amount_kobo', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('paystack_reference',)


@admin.register(CollectorPayout)
class CollectorPayoutAdmin(admin.ModelAdmin):
    list_display = (
        'collector', 'amount_kobo', 'status',
        'period_start', 'period_end', 'paid_at'
    )
    list_filter = ('status', 'period_start')
    search_fields = ('collector__phone', 'collector__name')
    raw_id_fields = ('collector',)
