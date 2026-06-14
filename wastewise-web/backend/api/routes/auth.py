"""
Authentication routes (OTP request, verification, token refresh).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from asgiref.sync import sync_to_async

from api import schemas, deps
from apps.users.models import User, OTPVerification

router = APIRouter()

@router.post('/request-otp/', response_model=schemas.MessageSchema)
async def request_otp(data: schemas.RequestOTPSchema):
    """
    Generate an OTP and send it via SMS (simulated for now).
    Creates a User if one doesn't exist.
    """
    phone = data.phone
    
    # 1. Ensure user exists
    user, created = await sync_to_async(User.objects.get_or_create)(
        phone=phone,
        defaults={'name': 'New User'}
    )
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    # 2. Generate OTP
    otp = await sync_to_async(OTPVerification.objects.create)(phone=phone)
    
    # 3. TODO: Send SMS via Africa's Talking
    # For development, just print it
    print(f"=============================")
    print(f"MOCK SMS to {phone}:")
    print(f"Your WasteWise code is {otp.code}")
    print(f"=============================")
    
    return {'message': 'OTP sent successfully'}


@router.post('/verify-otp/', response_model=schemas.TokenResponseSchema)
async def verify_otp(data: schemas.VerifyOTPSchema):
    """
    Verify the OTP and return JWT access/refresh tokens.
    """
    # 1. Find the latest OTP for this phone
    otp = await sync_to_async(
        lambda: OTPVerification.objects.filter(phone=data.phone).order_by('-created_at').first()
    )()
    
    if not otp:
        raise HTTPException(status_code=404, detail="No OTP found for this number")
        
    if not otp.is_valid:
        raise HTTPException(status_code=400, detail="OTP is expired or already used")
        
    if otp.code != data.code:
        # Hardcode a master code for easy testing if needed, e.g. "123456"
        if data.code != "123456":
            raise HTTPException(status_code=400, detail="Invalid OTP")
            
    # Mark as used
    otp.is_used = True
    await sync_to_async(otp.save)()
    
    # Get user
    try:
        user = await sync_to_async(User.objects.get)(phone=data.phone)
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Generate tokens
    access_token = deps.create_access_token(user.id)
    refresh_token = deps.create_refresh_token(user.id)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user
    }


@router.post('/refresh/', response_model=schemas.TokenResponseSchema)
async def refresh_token(data: schemas.RefreshTokenSchema):
    """
    Issue a new access token using a refresh token.
    """
    payload = deps.decode_token(data.refresh_token)
    
    if payload.get('type') != 'refresh':
        raise HTTPException(status_code=401, detail="Invalid token type")
        
    user_id = payload.get('sub')
    try:
        user = await sync_to_async(User.objects.get)(id=user_id)
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
        
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
        
    access_token = deps.create_access_token(user.id)
    refresh_token = deps.create_refresh_token(user.id)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user
    }


@router.get('/me/', response_model=schemas.UserSchema)
async def get_me(current_user: User = Depends(deps.get_current_user)):
    """
    Get the currently authenticated user's profile.
    """
    return current_user
