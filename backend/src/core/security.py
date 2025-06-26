"""
Security and Authentication

JWT token management, password hashing, and OAuth utilities.
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from src.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    """
    JWT Token data structure
    """

    sub: Optional[str]  # Subject (user ID)
    exp: Optional[datetime] = None  # Expiration time
    iat: Optional[datetime] = None  # Issued at
    token_type: str = "access"  # Token type (access/refresh)
    scopes: list = []  # Token scopes/permissions


class Token(BaseModel):
    """
    Token response model
    """

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int  # Seconds until expiration


def create_access_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None,
    scopes: list[str] | None = None,
) -> str:
    """
    Create JWT access token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "iat": datetime.utcnow(),
        "sub": str(subject),
        "token_type": "access",
        "scopes": scopes or [],
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    logger.debug(f"Created access token for subject: {subject}")
    return encoded_jwt


def create_refresh_token(subject: Union[str, int]) -> str:
    """
    Create JWT refresh token
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "exp": expire,
        "iat": datetime.utcnow(),
        "sub": str(subject),
        "token_type": "refresh",
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    logger.debug(f"Created refresh token for subject: {subject}")
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """
    Decode and validate JWT access token
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Validate token type
        if payload.get("token_type") != "access":
            raise JWTError("Invalid token type")

        # Extract token data
        token_data = TokenData(
            sub=payload.get("sub"),
            exp=datetime.fromtimestamp(payload.get("exp", 0)),
            iat=datetime.fromtimestamp(payload.get("iat", 0)),
            token_type=payload.get("token_type", "access"),
            scopes=payload.get("scopes", []),
        )

        # Check if token is expired
        if token_data.exp and datetime.utcnow() > token_data.exp:
            raise JWTError("Token expired")

        return token_data

    except JWTError as e:
        logger.warning(f"Token validation failed: {e}")
        raise JWTError(f"Could not validate credentials: {e}")


def decode_refresh_token(token: str) -> TokenData:
    """
    Decode and validate JWT refresh token
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Validate token type
        if payload.get("token_type") != "refresh":
            raise JWTError("Invalid token type")

        token_data = TokenData(
            sub=payload.get("sub"),
            exp=datetime.fromtimestamp(payload.get("exp", 0)),
            iat=datetime.fromtimestamp(payload.get("iat", 0)),
            token_type=payload.get("token_type", "refresh"),
        )

        # Check if token is expired
        if token_data.exp and datetime.utcnow() > token_data.exp:
            raise JWTError("Refresh token expired")

        return token_data

    except JWTError as e:
        logger.warning(f"Refresh token validation failed: {e}")
        raise JWTError(f"Could not validate refresh token: {e}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)


def generate_random_password(length: int = 12) -> str:
    """
    Generate a secure random password
    """
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_api_key() -> str:
    """
    Generate a secure API key
    """
    return secrets.token_urlsafe(32)


class PasswordValidator:
    """
    Password strength validator
    """

    @staticmethod
    def validate_password_strength(password: str) -> dict:
        """
        Validate password strength and return feedback
        """
        result: dict[str, Any] = {"valid": True, "score": 0, "feedback": []}

        # Length check
        if len(password) < 8:
            result["valid"] = False
            result["feedback"].append("Password must be at least 8 characters long")
        else:
            result["score"] += 1

        # Character type checks
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

        if not has_lower:
            result["feedback"].append("Password should contain lowercase letters")
        else:
            result["score"] += 1

        if not has_upper:
            result["feedback"].append("Password should contain uppercase letters")
        else:
            result["score"] += 1

        if not has_digit:
            result["feedback"].append("Password should contain numbers")
        else:
            result["score"] += 1

        if not has_special:
            result["feedback"].append("Password should contain special characters")
        else:
            result["score"] += 1

        # Common password check (simplified)
        common_passwords = ["password", "123456", "qwerty", "admin", "letmein"]
        if password.lower() in common_passwords:
            result["valid"] = False
            result["feedback"].append("Password is too common")

        # Final validation
        if result["score"] < 3:
            result["valid"] = False

        return result


class OAuth2Helper:
    """
    OAuth2 helper functions
    """

    @staticmethod
    def generate_state() -> str:
        """
        Generate OAuth2 state parameter
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def build_google_auth_url(state: str) -> str:
        """
        Build Google OAuth2 authorization URL
        """
        if not settings.GOOGLE_CLIENT_ID:
            raise ValueError("Google Client ID not configured")

        base_url = "https://accounts.google.com/o/oauth2/auth"
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": f"{settings.BACKEND_CORS_ORIGINS[0]}/auth/google/callback",
            "scope": "openid email profile",
            "response_type": "code",
            "state": state,
        }

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"

    @staticmethod
    def build_github_auth_url(state: str) -> str:
        """
        Build GitHub OAuth2 authorization URL
        """
        if not settings.GITHUB_CLIENT_ID:
            raise ValueError("GitHub Client ID not configured")

        base_url = "https://github.com/login/oauth/authorize"
        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": f"{settings.BACKEND_CORS_ORIGINS[0]}/auth/github/callback",
            "scope": "user:email",
            "state": state,
        }

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"


class SecurityHeaders:
    """
    Security headers for HTTP responses
    """

    @staticmethod
    def get_security_headers() -> dict:
        """
        Get recommended security headers
        """
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }


def create_token_pair(user_id: Union[str, int]) -> Token:
    """
    Create both access and refresh tokens
    """
    access_token = create_access_token(subject=user_id)
    refresh_token = create_refresh_token(subject=user_id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def refresh_access_token(refresh_token: str) -> Token:
    """
    Create new access token from refresh token
    """
    try:
        token_data = decode_refresh_token(refresh_token)
        if token_data.sub is None:
            raise JWTError("Invalid refresh token: no subject")

        new_access_token = create_access_token(subject=token_data.sub)

        return Token(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    except JWTError as e:
        logger.warning(f"Token refresh failed: {e}")
        raise JWTError("Invalid refresh token")
