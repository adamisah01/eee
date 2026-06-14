"""
Celery tasks for payments and payouts.
"""
from celery import shared_task
from django.utils import timezone
from apps.payments.models import Invoice


@shared_task
def send_payment_reminder(invoice_id):
    """
    Send an SMS reminder for unpaid invoices at 6h and 18h.
    """
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        if invoice.status == Invoice.Status.PENDING:
            # TODO: Send SMS via Africa's Talking
            print(f"SMS REMINDER: Please pay your WasteWise invoice {invoice.paystack_reference}")
            return "Reminder sent"
        return "Invoice already paid/expired"
    except Invoice.DoesNotExist:
        return "Invoice not found"


@shared_task
def expire_unpaid_invoice(invoice_id):
    """
    Mark invoice as expired after 24h.
    """
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        if invoice.status == Invoice.Status.PENDING and timezone.now() > invoice.expires_at:
            invoice.status = Invoice.Status.EXPIRED
            invoice.save()
            return "Invoice expired"
        return "Invoice not pending or not yet expired"
    except Invoice.DoesNotExist:
        return "Invoice not found"


@shared_task
def process_weekly_payouts():
    """
    Weekly beat task to calculate and execute Paystack transfers to collectors.
    """
    # Logic to aggregate un-paid completed jobs for each collector
    # and hit Paystack Transfer API
    return "Payouts processed"
