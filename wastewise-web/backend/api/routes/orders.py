"""
Orders routes for WasteWise REST API.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from asgiref.sync import sync_to_async
from typing import List

from api import schemas, deps
from apps.users.models import User
from apps.orders.models import PickupOrder, WasteCategory

router = APIRouter()

@router.post('/', response_model=schemas.OrderSummarySchema)
async def create_order(
    data: schemas.CreateOrderSchema,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Create a new pickup order.
    """
    # Verify category
    try:
        category = await sync_to_async(WasteCategory.objects.get)(slug=data.category_slug)
    except WasteCategory.DoesNotExist:
        raise HTTPException(status_code=404, detail="Waste category not found")

    # Create the order
    order = await sync_to_async(PickupOrder.objects.create)(
        customer=current_user,
        category=category,
        address=data.address,
        latitude=data.latitude,
        longitude=data.longitude,
        scheduled_time=data.scheduled_time,
        is_immediate=data.is_immediate,
        special_instructions=data.special_instructions,
        status=PickupOrder.Status.PENDING
    )
    
    # TODO: Trigger Celery task to assign nearest collector if is_immediate=True
    
    return {
        'id': str(order.id),
        'order_number': order.order_number,
        'category_name': category.name,
        'category_icon': category.icon,
        'status': order.status,
        'address': order.address,
        'created_at': order.created_at
    }


@router.get('/', response_model=schemas.PaginatedResponse)
async def list_orders(
    page: int = 1,
    status: str = None,
    current_user: User = Depends(deps.get_current_user)
):
    """
    List orders for the current user.
    """
    page_size = 20
    offset = (page - 1) * page_size
    
    def fetch_orders():
        qs = PickupOrder.objects.filter(customer=current_user).select_related('category', 'invoice')
        if status:
            qs = qs.filter(status=status)
        count = qs.count()
        orders = list(qs[offset:offset + page_size])
        
        results = []
        for o in orders:
            total_amount = o.invoice.total_amount_kobo if hasattr(o, 'invoice') else None
            results.append({
                'id': str(o.id),
                'order_number': o.order_number,
                'category_name': o.category.name,
                'category_icon': o.category.icon,
                'status': o.status,
                'address': o.address,
                'created_at': o.created_at,
                'weight_kg': float(o.weight_kg) if o.weight_kg else None,
                'rating': o.rating,
                'total_amount_kobo': total_amount
            })
        return count, results

    count, results = await sync_to_async(fetch_orders)()
    
    return {
        'count': count,
        'page': page,
        'page_size': page_size,
        'results': results
    }


@router.get('/{order_number}/', response_model=schemas.OrderDetailSchema)
async def get_order_detail(
    order_number: str,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get detailed view of a specific order.
    """
    def fetch_order_detail():
        try:
            o = PickupOrder.objects.select_related(
                'category', 'collector', 'collector__collector_profile', 'invoice'
            ).prefetch_related('status_logs').get(
                order_number=order_number, customer=current_user
            )
            
            logs = [
                {
                    'status': log.to_status,
                    'timestamp': log.timestamp,
                    'notes': log.notes
                }
                for log in o.status_logs.all().order_by('timestamp')
            ]
            
            # Basic initial log
            if not logs:
                 logs = [{'status': PickupOrder.Status.PENDING, 'timestamp': o.created_at, 'notes': 'Order created'}]
            
            total_amount = o.invoice.total_amount_kobo if hasattr(o, 'invoice') else None
            
            col_name = col_phone = col_rating = col_vehicle = None
            if o.collector:
                col_name = o.collector.name
                col_phone = o.collector.phone
                if hasattr(o.collector, 'collector_profile'):
                    col_rating = float(o.collector.collector_profile.rating)
                    col_vehicle = o.collector.collector_profile.get_vehicle_type_display()
            
            return {
                'id': str(o.id),
                'order_number': o.order_number,
                'category_name': o.category.name,
                'category_icon': o.category.icon,
                'status': o.status,
                'address': o.address,
                'latitude': float(o.latitude) if o.latitude else None,
                'longitude': float(o.longitude) if o.longitude else None,
                'scheduled_time': o.scheduled_time,
                'is_immediate': o.is_immediate,
                'special_instructions': o.special_instructions,
                'created_at': o.created_at,
                'assigned_at': o.assigned_at,
                'completed_at': o.completed_at,
                'weight_kg': float(o.weight_kg) if o.weight_kg else None,
                'rating': o.rating,
                'total_amount_kobo': total_amount,
                'collector_name': col_name,
                'collector_phone': col_phone,
                'collector_rating': col_rating,
                'collector_vehicle': col_vehicle,
                'status_timeline': logs
            }
        except PickupOrder.DoesNotExist:
            return None

    detail = await sync_to_async(fetch_order_detail)()
    if not detail:
        raise HTTPException(status_code=404, detail="Order not found")
        
    return detail


@router.post('/{order_number}/rate/', response_model=schemas.MessageSchema)
async def rate_order(
    order_number: str,
    data: schemas.RateOrderSchema,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Rate a completed order.
    """
    try:
        order = await sync_to_async(PickupOrder.objects.get)(
            order_number=order_number, 
            customer=current_user
        )
    except PickupOrder.DoesNotExist:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order.status not in (PickupOrder.Status.PAID, PickupOrder.Status.COMPLETED, PickupOrder.Status.PAYMENT_PENDING):
         raise HTTPException(status_code=400, detail="Can only rate completed orders")
         
    order.rating = data.rating
    order.rating_comment = data.comment
    await sync_to_async(order.save)()
    
    # TODO: Update collector's overall rating
    
    return {'message': 'Rating submitted successfully'}
