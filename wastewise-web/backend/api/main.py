"""
FastAPI application for WasteWise REST API.
Mounted at /api/ via the ASGI router in core/asgi.py.
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from django.conf import settings

from api.routes import auth, orders, collectors, payments

app = FastAPI(
    title='WasteWise API',
    description='On-demand waste collection platform API',
    version='1.0.0',
    docs_url='/api/docs',
    redoc_url='/api/redoc',
    openapi_url='/api/openapi.json',
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Mount route modules
app.include_router(auth.router, prefix='/api/auth', tags=['Authentication'])
app.include_router(orders.router, prefix='/api/orders', tags=['Orders'])
app.include_router(collectors.router, prefix='/api/collectors', tags=['Collectors'])
app.include_router(payments.router, prefix='/api/payments', tags=['Payments'])


@app.get('/api/health')
async def health_check():
    return {'status': 'healthy', 'service': 'WasteWise API'}
