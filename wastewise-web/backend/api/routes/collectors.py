"""
Collectors routes for WasteWise REST API.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from asgiref.sync import sync_to_async
from django.utils import timezone
from typing import List

from api import schemas, deps
from apps.users.models import User
from apps.collectors.models import CollectorProfile, CollectorLocationHistory
from apps.orders.models import PickupOrder, OrderStatusLog

router = APIRouter()

@router.post('/status/', response_model=schemas.MessageSchema)
async def toggle_status(
    data: schemas.ToggleStatusSchema,
    current_collector: User = Depends(deps.get_current_collector)
):
    """
    Toggle collector online/offline status.
    """
    def update_status():
        try:
            profile = current_collector.collector_profile
        except CollectorProfile.DoesNotExist:
            profile = CollectorProfile.objects.create(user=current_collector)
            
        profile.is_online = data.is_online
        if data.is_online and data.latitude and data.longitude:
            profile.current_latitude = data.latitude
            profile.current_longitude = data.longitude
            profile.last_location_update = timezone.now()
        profile.save()
        return profile.is_online

    is_online = await sync_to_async(update_status)()
    status_str = "online" if is_online else "offline"
    return {'message': f'You are now {status_str}'}


@router.post('/location/', response_model=schemas.MessageSchema)
async def update_location(
    data: schemas.UpdateLocationSchema,
    current_collector: User = Depends(deps.get_current_collector)
):
    """
    Update collector GPS location (called periodically when active).
    """
    def save_location():
        try:
            profile = current_collector.collector_profile
        except CollectorProfile.DoesNotExist:
            return False
            
        profile.current_latitude = data.latitude
        profile.current_longitude = data.longitude
        profile.last_location_update = timezone.now()
        profile.save()
        
        # If on an active job, log history
        active_job = PickupOrder.objects.filter(
            collector=current_collector,
            status__in=[
                PickupOrder.Status.ASSIGNED, 
                PickupOrder.Status.EN_ROUTE, 
                PickupOrder.Status.ARRIVED, 
                PickupOrder.Status.COLLECTING
            ]
        ).first()
        
        if active_job:
            CollectorLocationHistory.objects.create(
                collector=profile,
                latitude=data.latitude,
                longitude=data.longitude
            )
            # TODO: Send WebSocket update to customer
            
        return True

    success = await sync_to_async(save_location)()
    if not success:
         raise HTTPException(status_code=400, detail="Collector profile not found")
         
    return {'message': 'Location updated'}


@router.get('/active-job/', response_model=schemas.OrderDetailSchema)
async def get_active_job(
    current_collector: User = Depends(deps.get_current_collector)
):
    """
    Get the collector's currently active job.
    """
    def fetch_job():
        try:
            o = PickupOrder.objects.select_related('category', 'customer').get(
                collector=current_collector,
                status__in=[
                    PickupOrder.Status.ASSIGNED, 
                    PickupOrder.Status.EN_ROUTE, 
                    PickupOrder.Status.ARRIVED, 
                    PickupOrder.Status.COLLECTING
                ]
            )
            
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
                'customer_name': o.customer.name,
                'customer_phone': o.customer.phone,
                'status_timeline': [] # Can populate if needed
            }
        except PickupOrder.DoesNotExist:
            return None

    job = await sync_to_async(fetch_job)()
    if not job:
         raise HTTPException(status_code=404, detail="No active job")
         
    return job


@router.post('/jobs/{order_number}/update-status/', response_model=schemas.MessageSchema)
async def update_job_status(
    order_number: str,
    data: schemas.UpdateJobStatusSchema,
    current_collector: User = Depends(deps.get_current_collector)
):
    """
    Progress a job through its statuses.
    """
    def update_status():
        try:
            order = PickupOrder.objects.get(
                order_number=order_number, 
                collector=current_collector
            )
        except PickupOrder.DoesNotExist:
            return False, "Job not found"
            
        old_status = order.status
        new_status = data.status
        
        # Validation could be added here for correct status transitions
        
        order.status = new_status
        if new_status == PickupOrder.Status.COMPLETED:
            order.completed_at = timezone.now()
            # If weight is provided
            if data.weight_kg:
                 order.weight_kg = data.weight_kg
                 
            # TODO: Generate Invoice via Celery
            
        order.save()
        
        OrderStatusLog.objects.create(
            order=order,
            from_status=old_status,
            to_status=new_status,
            changed_by=current_collector
        )
        
        # TODO: Send WebSocket update to customer
        
        return True, "Status updated"

    success, message = await sync_to_async(update_status)()
    if not success:
         raise HTTPException(status_code=400, detail=message)
         
    return {'message': message}


@router.get('/earnings/', response_model=schemas.EarningsSummarySchema)
async def get_earnings(
    current_collector: User = Depends(deps.get_current_collector)
):
    """
    Get collector earnings summary.
    """
    def fetch_earnings():
        try:
            profile = current_collector.collector_profile
            # Simplified for now. A real app would sum invoices.
            return {
                'today_kobo': 0,
                'this_week_kobo': 0,
                'pending_kobo': 0,
                'total_kobo': profile.total_earnings_kobo,
                'total_jobs': profile.total_jobs
            }
        except CollectorProfile.DoesNotExist:
            return None

    earnings = await sync_to_async(fetch_earnings)()
    if not earnings:
         return schemas.EarningsSummarySchema()
    return earnings
