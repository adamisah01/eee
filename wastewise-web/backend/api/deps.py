"""
Dependency injection for FastAPI routes.
Handles JWT authentication, current user extraction, and Django ORM access.
"""
import os
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Django ORM setup
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from apps.users.models import User

security = HTTPBearer()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'


def create_access_token(user_id: str) -> str:
    """Create a JWT access token."""
    payload = {
        'sub': str(user_id),
        'type': 'access',
        'exp': datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_LIFETIME_MINUTES
        ),
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Create a JWT refresh token."""
    payload = {
        'sub': str(user_id),
        'type': 'refresh',
        'exp': datetime.now(timezone.utc) + timedelta(
            days=settings.JWT_REFRESH_TOKEN_LIFETIME_DAYS
        ),
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token has expired'
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token'
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Extract and validate the current user from the JWT token."""
    payload = decode_token(credentials.credentials)

    if payload.get('type') != 'access':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token type'
        )

    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token payload'
        )

    try:
        from asgiref.sync import sync_to_async
        user = await sync_to_async(User.objects.get)(id=user_id)
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found'
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User account is disabled'
        )

    return user


async def get_current_collector(
    user: User = Depends(get_current_user)
) -> User:
    """Ensure the current user is a collector."""
    if user.role != User.Role.COLLECTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Collector access required'
        )
    return user
