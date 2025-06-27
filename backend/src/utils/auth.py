"""
Authentication and Authorization Utilities

JWT token handling, password hashing, and permission checking utilities.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext

from core.config import settings
from models.user import User
from schemas.auth import TokenData

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing failed: {e}")
        raise


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    try:
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire, "type": "access"})

        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

        return encoded_jwt

    except Exception as e:
        logger.error(f"Failed to create access token: {e}")
        raise


def create_refresh_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT refresh token"""
    try:
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )

        to_encode.update({"exp": expire, "type": "refresh"})

        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

        return encoded_jwt

    except Exception as e:
        logger.error(f"Failed to create refresh token: {e}")
        raise


def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Check token type
        if payload.get("type") != token_type:
            return None

        # Extract token data
        user_id: int = payload.get("user_id")
        username: str = payload.get("username")
        email: str = payload.get("email")
        role: str = payload.get("role")
        scopes: List[str] = payload.get("scopes", [])

        if user_id is None:
            return None

        return TokenData(
            user_id=user_id, username=username, email=email, role=role, scopes=scopes
        )

    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return None


def create_tokens_for_user(user: User) -> Dict[str, Union[str, int]]:
    """Create access and refresh tokens for user"""
    try:
        if not hasattr(user, "role") or user.role is None:
            raise ValueError("User role is missing or invalid.")

        # Token payload
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "scopes": get_user_scopes(user.role.value),
        }

        # Create tokens
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"user_id": user.id})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    except Exception as e:
        logger.error(f"Failed to create tokens for user {user.id}: {e}")
        raise


def get_user_scopes(role: str) -> List[str]:
    """Get user scopes based on role"""
    role_scopes = {
        "admin": [
            "users:read",
            "users:write",
            "users:delete",
            "projects:read",
            "projects:write",
            "projects:delete",
            "tasks:read",
            "tasks:write",
            "tasks:delete",
            "calendar:read",
            "calendar:write",
            "calendar:delete",
            "system:read",
            "system:write",
        ],
        "project_manager": [
            "users:read",
            "projects:read",
            "projects:write",
            "tasks:read",
            "tasks:write",
            "tasks:delete",
            "calendar:read",
            "calendar:write",
        ],
        "developer": [
            "users:read",
            "projects:read",
            "tasks:read",
            "tasks:write",
            "calendar:read",
            "calendar:write",
        ],
        "viewer": ["users:read", "projects:read", "tasks:read", "calendar:read"],
    }

    return role_scopes.get(role, ["projects:read", "tasks:read"])


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[TokenData]:
    """Get current user from token (optional - no error if no token)"""
    if not credentials:
        return None

    token_data = verify_token(credentials.credentials)
    return token_data


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    """Get current user from token (required)"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = verify_token(credentials.credentials)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user),
) -> TokenData:
    """Get current active user (additional validation can be added here)"""
    # Additional user validation could be performed here
    # For example, checking if user is still active in database
    return current_user


def require_scopes(required_scopes: List[str]):
    """Decorator to require specific scopes"""

    def scope_checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if not current_user.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )

        for scope in required_scopes:
            if scope not in current_user.scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required scope: {scope}",
                )

        return current_user

    return scope_checker


def require_roles(required_roles: List[str]):
    """Decorator to require specific roles"""

    def role_checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role permissions",
            )

        return current_user

    return role_checker


def check_permission(user_role: str, resource: str, action: str) -> bool:
    """Check if user role has permission for resource and action"""
    user_scopes = get_user_scopes(user_role)
    required_scope = f"{resource}:{action}"

    return required_scope in user_scopes


def generate_reset_token(user_id: int) -> str:
    """Generate password reset token"""
    try:
        data = {
            "user_id": user_id,
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1),  # 1 hour expiry
        }

        token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        return token

    except Exception as e:
        logger.error(f"Failed to generate reset token: {e}")
        raise


def verify_reset_token(token: str) -> Optional[int]:
    """Verify password reset token and return user ID"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        if payload.get("type") != "password_reset":
            return None

        user_id: int = payload.get("user_id")
        return user_id

    except jwt.ExpiredSignatureError:
        logger.warning("Reset token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid reset token: {e}")
        return None
    except Exception as e:
        logger.error(f"Reset token verification failed: {e}")
        return None


def generate_email_verification_token(user_id: int, email: str) -> str:
    """Generate email verification token"""
    try:
        data = {
            "user_id": user_id,
            "email": email,
            "type": "email_verification",
            "exp": datetime.utcnow() + timedelta(days=7),  # 7 days expiry
        }

        token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        return token

    except Exception as e:
        logger.error(f"Failed to generate email verification token: {e}")
        raise


def verify_email_verification_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify email verification token"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        if payload.get("type") != "email_verification":
            return None

        return {"user_id": payload.get("user_id"), "email": payload.get("email")}

    except jwt.ExpiredSignatureError:
        logger.warning("Email verification token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid email verification token: {e}")
        return None
    except Exception as e:
        logger.error(f"Email verification token verification failed: {e}")
        return None


class AuthManager:
    """Authentication manager class"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return get_password_hash(password)

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return verify_password(password, hashed)

    @staticmethod
    def create_tokens(user: User) -> Dict[str, Union[str, int]]:
        """Create authentication tokens for user"""
        return create_tokens_for_user(user)

    @staticmethod
    def verify_access_token(token: str) -> Optional[TokenData]:
        """Verify access token"""
        return verify_token(token, "access")

    @staticmethod
    def verify_refresh_token(token: str) -> Optional[TokenData]:
        """Verify refresh token"""
        return verify_token(token, "refresh")

    @staticmethod
    def generate_password_reset_token(user_id: int) -> str:
        """Generate password reset token"""
        return generate_reset_token(user_id)

    @staticmethod
    def verify_password_reset_token(token: str) -> Optional[int]:
        """Verify password reset token"""
        return verify_reset_token(token)

    @staticmethod
    def generate_email_verification_token(user_id: int, email: str) -> str:
        """Generate email verification token"""
        return generate_email_verification_token(user_id, email)

    @staticmethod
    def verify_email_verification_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify email verification token"""
        return verify_email_verification_token(token)
