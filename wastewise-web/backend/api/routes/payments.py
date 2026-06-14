"""
Payments routes for WasteWise REST API.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from asgiref.sync import sync_to_async

from api import schemas, deps
from apps.users.models import User
from apps.orders.models import PickupOrder
from apps.payments.models import Invoice, Transaction

router = APIRouter()

@router.get('/invoice/{order_number}/', response_model=schemas.InvoiceSchema)
async def get_invoice(
    order_number: str,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get the invoice for a completed order.
    """
    def fetch_invoice():
        try:
            invoice = Invoice.objects.select_related('order').get(
                order__order_number=order_number, 
                customer=current_user
            )
            return {
                'id': str(invoice.id),
                'order_number': invoice.order.order_number,
                'base_amount_kobo': invoice.base_amount_kobo,
                'weight_charge_kobo': invoice.weight_charge_kobo,
                'platform_fee_kobo': invoice.platform_fee_kobo,
                'total_amount_kobo': invoice.total_amount_kobo,
                'paystack_reference': invoice.paystack_reference,
                'status': invoice.status,
                'expires_at': invoice.expires_at,
                'paid_at': invoice.paid_at
            }
        except Invoice.DoesNotExist:
            return None

    invoice = await sync_to_async(fetch_invoice)()
    if not invoice:
         raise HTTPException(status_code=404, detail="Invoice not found")
         
    return invoice


@router.post('/verify/{reference}/', response_model=schemas.MessageSchema)
async def verify_payment(
    reference: str,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Verify a Paystack payment. In a real app, this would call the Paystack API.
    """
    def process_verification():
        try:
            invoice = Invoice.objects.select_related('order').get(
                paystack_reference=reference,
                customer=current_user
            )
        except Invoice.DoesNotExist:
            return False, "Invoice not found"
            
        if invoice.status == Invoice.Status.PAID:
             return True, "Payment already verified"
             
        # MOCK PAYSTACK VERIFICATION
        # In a real app: httpx.get(f"https://api.paystack.co/transaction/verify/{reference}")
        
        # 1. Update Invoice
        from django.utils import timezone
        invoice.status = Invoice.Status.PAID
        invoice.paid_at = timezone.now()
        invoice.save()
        
        # 2. Record Transaction
        Transaction.objects.create(
            invoice=invoice,
            paystack_reference=reference,
            amount_kobo=invoice.total_amount_kobo,
            status=Transaction.Status.SUCCESS
        )
        
        # 3. Update Order Status
        order = invoice.order
        order.status = PickupOrder.Status.PAID
        order.save()
        
        # 4. Update Collector Earnings
        if order.collector and hasattr(order.collector, 'collector_profile'):
             profile = order.collector.collector_profile
             profile.total_earnings_kobo += (invoice.base_amount_kobo + invoice.weight_charge_kobo)
             profile.total_jobs += 1
             profile.save()
             
        return True, "Payment verified successfully"

    success, message = await sync_to_async(process_verification)()
    if not success:
         raise HTTPException(status_code=400, detail=message)
         
    return {'message': message}


@router.get('/history/', response_model=schemas.PaginatedResponse)
async def get_payment_history(
    page: int = 1,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get customer's payment history.
    """
    page_size = 20
    offset = (page - 1) * page_size
    
    def fetch_history():
        qs = Transaction.objects.filter(
            invoice__customer=current_user,
            status=Transaction.Status.SUCCESS
        ).select_related('invoice', 'invoice__order').order_by('-created_at')
        
        count = qs.count()
        txns = list(qs[offset:offset + page_size])
        
        results = []
        for t in txns:
            results.append({
                'order_number': t.invoice.order.order_number,
                'amount_kobo': t.amount_kobo,
                'status': t.status,
                'paid_at': t.invoice.paid_at,
                'created_at': t.created_at
            })
        return count, results

    count, results = await sync_to_async(fetch_history)()
    
    return {
        'count': count,
        'page': page,
        'page_size': page_size,
        'results': results
    }
