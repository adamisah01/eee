"""
URL configuration for WasteWise Django backend.
API is handled by FastAPI via ASGI router.
This file handles Django Admin and WebSocket routing.
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = 'WasteWise Admin'
admin.site.site_title = 'WasteWise'
admin.site.index_title = 'Dashboard'

urlpatterns = [
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
