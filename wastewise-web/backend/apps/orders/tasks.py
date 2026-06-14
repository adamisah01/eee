"""
Celery tasks for orders.
"""
from celery import shared_task
from django.utils import timezone
from apps.orders.models import PickupOrder
from apps.collectors.models import CollectorProfile
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@shared_task
def assign_nearest_collector(order_id):
    """
    Finds the nearest online collector and assigns the order to them.
    In a real app, this uses PostGIS ST_Distance. Here we mock the logic.
    """
    try:
        order = PickupOrder.objects.get(id=order_id)
        if order.status != PickupOrder.Status.PENDING:
            return "Order not pending"
            
        # Mock: just pick the first online collector
        collector_profile = CollectorProfile.objects.filter(is_online=True).first()
        
        if collector_profile:
            collector = collector_profile.user
            order.collector = collector
            order.status = PickupOrder.Status.ASSIGNED
            order.assigned_at = timezone.now()
            order.save()
            
            # Notify the collector via WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'collector_{collector.id}_jobs',
                {
                    'type': 'new_job',
                    'order': {
                        'order_number': order.order_number,
                        'category_name': order.category.name,
                        'address': order.address,
                        'latitude': float(order.latitude) if order.latitude else None,
                        'longitude': float(order.longitude) if order.longitude else None,
                    }
                }
            )
            return f"Assigned to {collector.phone}"
        else:
            # Requeue or notify admin
            return "No online collectors available"
    except PickupOrder.DoesNotExist:
        return "Order not found"
