"""
Authentication Pydantic Schemas

Request/Response schemas for authentication and authorization.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class TokenData(BaseModel):
    """Token data schema"""

    user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    scopes: List[str] = []


class Token(BaseModel):
    """Token schema"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Token refresh schema"""

    refresh_token: str = Field(..., description="Refresh token")


class LoginRequest(BaseModel):
    """Login request schema"""

    username_or_email: str = Field(..., description="Username or email address")
    password: str = Field(..., description="Password")
    remember_me: bool = Field(default=False, description="Remember login")


class UserResponse(BaseModel):
    """User response schema"""

    id: int
    name: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    status: str
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = (
            True  # For Pydantic v2, use from_attributes instead of orm_mode
        )


class LoginResponse(BaseModel):
    """Login response schema"""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")


class RegisterRequest(BaseModel):
    """User registration request schema"""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    full_name: Optional[str] = Field(None, max_length=200, description="Full name")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""

    refresh_token: str = Field(..., description="Refresh token")


class RefreshTokenResponse(BaseModel):
    """Refresh token response schema"""

    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class LogoutRequest(BaseModel):
    """Logout request schema"""

    token: Optional[str] = Field(None, description="Token to blacklist (optional)")
    logout_all: bool = Field(default=False, description="Logout from all devices")


class PasswordChangeRequest(BaseModel):
    """Password change request schema"""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match")
        return v

    @validator("new_password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""

    email: EmailStr = Field(..., description="Email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""

    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match")
        return v

    @validator("new_password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class EmailVerificationRequest(BaseModel):
    """Email verification request schema"""

    token: str = Field(..., description="Email verification token")


class TwoFactorSetupRequest(BaseModel):
    """Two-factor authentication setup request schema"""

    password: str = Field(..., description="User password for verification")


class TwoFactorSetupResponse(BaseModel):
    """Two-factor authentication setup response schema"""

    secret_key: str
    qr_code_url: str
    backup_codes: List[str]


class TwoFactorVerifyRequest(BaseModel):
    """Two-factor authentication verification request schema"""

    token: str = Field(
        ..., min_length=6, max_length=6, description="6-digit TOTP token"
    )

    @validator("token")
    def validate_token(cls, v):
        if not v.isdigit():
            raise ValueError("Token must be 6 digits")
        return v


class TwoFactorDisableRequest(BaseModel):
    """Two-factor authentication disable request schema"""

    password: str = Field(..., description="User password for verification")
    token: str = Field(
        ..., min_length=6, max_length=6, description="6-digit TOTP token"
    )

    @validator("token")
    def validate_token(cls, v):
        if not v.isdigit():
            raise ValueError("Token must be 6 digits")
        return v


class OAuthProvider:
    """OAuth provider enum"""

    GOOGLE = "google"
    GITHUB = "github"
    MICROSOFT = "microsoft"
    FACEBOOK = "facebook"


class OAuthLoginRequest(BaseModel):
    """OAuth login request schema"""

    provider: str = Field(..., description="OAuth provider")
    code: str = Field(..., description="Authorization code")
    state: Optional[str] = Field(None, description="State parameter")

    @validator("provider")
    def validate_provider(cls, v):
        valid_providers = ["google", "github", "microsoft", "facebook"]
        if v not in valid_providers:
            raise ValueError(f'Provider must be one of: {", ".join(valid_providers)}')
        return v


class OAuthLinkRequest(BaseModel):
    """OAuth account linking request schema"""

    provider: str = Field(..., description="OAuth provider")
    code: str = Field(..., description="Authorization code")

    @validator("provider")
    def validate_provider(cls, v):
        valid_providers = ["google", "github", "microsoft", "facebook"]
        if v not in valid_providers:
            raise ValueError(f'Provider must be one of: {", ".join(valid_providers)}')
        return v


class OAuthUnlinkRequest(BaseModel):
    """OAuth account unlinking request schema"""

    provider: str = Field(..., description="OAuth provider")

    @validator("provider")
    def validate_provider(cls, v):
        valid_providers = ["google", "github", "microsoft", "facebook"]
        if v not in valid_providers:
            raise ValueError(f'Provider must be one of: {", ".join(valid_providers)}')
        return v


class SessionResponse(BaseModel):
    """Session response schema"""

    id: int
    user_id: int
    session_token: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_activity: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """Session list response schema"""

    sessions: List[SessionResponse]
    current_session_id: int


class RolePermission(BaseModel):
    """Role permission schema"""

    resource: str = Field(..., description="Resource name")
    actions: List[str] = Field(..., description="Allowed actions")


class RoleResponse(BaseModel):
    """Role response schema"""

    id: int
    name: str
    description: Optional[str] = None
    permissions: List[RolePermission] = []
    is_system_role: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class PermissionCheck(BaseModel):
    """Permission check schema"""

    resource: str = Field(..., description="Resource name")
    action: str = Field(..., description="Action to check")


class PermissionResponse(BaseModel):
    """Permission response schema"""

    has_permission: bool
    reason: Optional[str] = None


class SecuritySettings(BaseModel):
    """Security settings schema"""

    two_factor_enabled: bool = False
    password_last_changed: Optional[datetime] = None
    login_attempts: int = 0
    account_locked_until: Optional[datetime] = None
    oauth_providers: List[str] = []
    active_sessions: int = 0


class AuditLogResponse(BaseModel):
    """Audit log response schema"""

    id: int
    user_id: Optional[int] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Audit log list response schema"""

    logs: List[AuditLogResponse]
    total: int
    page: int
    per_page: int
    pages: int


class SecurityEventResponse(BaseModel):
    """Security event response schema"""

    id: int
    user_id: Optional[int] = None
    event_type: str
    severity: str
    description: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True
