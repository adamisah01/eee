"""
WebSocket routing configuration.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/order/(?P<order_id>[a-zA-Z0-9_-]+)/track/$', consumers.OrderTrackingConsumer.as_asgi()),
    re_path(r'ws/collector/jobs/$', consumers.CollectorJobConsumer.as_asgi()),
]
