"""
Django Channels WebSocket consumers for real-time features.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
import jwt

# We need a quick helper to authenticate websocket connections
# since they don't have standard HTTP headers, we typically pass a token in the query string or initial message.

@database_sync_to_async
def get_user_from_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        from apps.users.models import User
        return User.objects.get(id=payload['sub'])
    except Exception:
        return None

class OrderTrackingConsumer(AsyncWebsocketConsumer):
    """
    Consumer for customers tracking their order.
    Receives GPS updates from the assigned collector.
    """
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'order_{self.order_id}_track'

        # Optional: authenticate connection
        query_string = self.scope['query_string'].decode()
        token = None
        if 'token=' in query_string:
             token = query_string.split('token=')[1].split('&')[0]
             
        self.user = None
        if token:
             self.user = await get_user_from_token(token)

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from room group
    async def gps_update(self, event):
        """Called when a collector sends a GPS update."""
        latitude = event['latitude']
        longitude = event['longitude']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'gps_update',
            'latitude': latitude,
            'longitude': longitude
        }))
        
    async def status_update(self, event):
        """Called when order status changes."""
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': event['status']
        }))


class CollectorJobConsumer(AsyncWebsocketConsumer):
    """
    Consumer for collectors waiting for new jobs.
    """
    async def connect(self):
        query_string = self.scope['query_string'].decode()
        token = None
        if 'token=' in query_string:
             token = query_string.split('token=')[1].split('&')[0]
             
        self.user = None
        if token:
             self.user = await get_user_from_token(token)
             
        if not self.user or self.user.role != 'collector':
             await self.close()
             return

        self.room_group_name = f'collector_{self.user.id}_jobs'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
             await self.channel_layer.group_discard(
                 self.room_group_name,
                 self.channel_name
             )

    async def new_job(self, event):
        """Called by Celery task when a job is assigned."""
        await self.send(text_data=json.dumps({
            'type': 'new_job',
            'order': event['order']
        }))
