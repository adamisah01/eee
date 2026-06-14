"""
Pydantic schemas for all API request/response bodies.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ─── Auth ────────────────────────────────────────────────────────────────────

class RequestOTPSchema(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15, examples=['+2348031234567'])

class VerifyOTPSchema(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)
    code: str = Field(..., min_length=6, max_length=6)

class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
    user: 'UserSchema'

class RefreshTokenSchema(BaseModel):
    refresh_token: str

class UserSchema(BaseModel):
    id: str
    phone: str
    name: str
    email: str
    role: str
    address: str
    lga: str

    class Config:
        from_attributes = True


# ─── Orders ──────────────────────────────────────────────────────────────────

class CreateOrderSchema(BaseModel):
    category_slug: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    scheduled_time: Optional[datetime] = None
    is_immediate: bool = True
    special_instructions: str = ''

class OrderStatusEnum(str, Enum):
    pending = 'pending'
    assigned = 'assigned'
    en_route = 'en_route'
    arrived = 'arrived'
    collecting = 'collecting'
    completed = 'completed'
    payment_pending = 'payment_pending'
    paid = 'paid'
    cancelled = 'cancelled'

class OrderSummarySchema(BaseModel):
    id: str
    order_number: str
    category_name: str
    category_icon: str
    status: str
    address: str
    created_at: datetime
    weight_kg: Optional[float] = None
    rating: Optional[int] = None
    total_amount_kobo: Optional[int] = None

class OrderDetailSchema(OrderSummarySchema):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    scheduled_time: Optional[datetime] = None
    is_immediate: bool
    special_instructions: str
    collector_name: Optional[str] = None
    collector_phone: Optional[str] = None
    collector_rating: Optional[float] = None
    collector_vehicle: Optional[str] = None
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status_timeline: List[dict] = []

class RateOrderSchema(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str = ''


# ─── Collector ───────────────────────────────────────────────────────────────

class ToggleStatusSchema(BaseModel):
    is_online: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UpdateLocationSchema(BaseModel):
    latitude: float
    longitude: float

class UpdateJobStatusSchema(BaseModel):
    status: str = Field(..., description='Next status: en_route, arrived, collecting, completed')
    weight_kg: Optional[float] = None

class EarningsSummarySchema(BaseModel):
    today_kobo: int = 0
    this_week_kobo: int = 0
    pending_kobo: int = 0
    total_kobo: int = 0
    total_jobs: int = 0

class JobHistoryItemSchema(BaseModel):
    order_number: str
    category_name: str
    address: str
    earnings_kobo: int
    completed_at: Optional[datetime] = None


# ─── Payments ────────────────────────────────────────────────────────────────

class InvoiceSchema(BaseModel):
    id: str
    order_number: str
    base_amount_kobo: int
    weight_charge_kobo: int
    platform_fee_kobo: int
    total_amount_kobo: int
    paystack_reference: str
    status: str
    expires_at: datetime
    paid_at: Optional[datetime] = None

class VerifyPaymentSchema(BaseModel):
    reference: str

class PaymentHistoryItemSchema(BaseModel):
    order_number: str
    amount_kobo: int
    status: str
    paid_at: Optional[datetime] = None
    created_at: datetime


# ─── Generic ─────────────────────────────────────────────────────────────────

class MessageSchema(BaseModel):
    message: str
    success: bool = True

class PaginatedResponse(BaseModel):
    count: int
    page: int
    page_size: int
    results: list
