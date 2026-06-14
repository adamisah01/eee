"""
Celery app configuration for WasteWise backend.
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('wastewise')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks([
    'apps.orders',
    'apps.payments',
    'apps.notifications',
])
