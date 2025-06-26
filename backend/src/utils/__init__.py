"""
Utilities Package

Common utilities and helper functions for the PMS application.
"""

from .auth import *
from .exceptions import *
from .field_updater import *
from .helper import *
from .logger import LoggerMixin, StructuredLogger, get_logger, setup_logging

# Import log functions separately to avoid circular imports
try:
    from utils.logger import log_audit_event, log_security_event
except ImportError:
    # Fallback functions if not available
    def log_audit_event(*args, **kwargs):
        pass

    def log_security_event(*args, **kwargs):
        pass


__all__ = [
    # Auth utilities
    "AuthManager",
    "create_access_token",
    "create_refresh_token",
    "get_current_user",
    "get_password_hash",
    "require_roles",
    "require_scopes",
    "verify_password",
    "verify_token",
    # Exception classes
    "AuthenticationError",
    "AuthorizationError",
    "BaseAPIException",
    "BusinessLogicError",
    "ConflictError",
    "DatabaseError",
    "NotFoundError",
    "ValidationError",
    # Logger utilities
    "LoggerMixin",
    "StructuredLogger",
    "get_logger",
    "setup_logging",
    "log_audit_event",
    "log_security_event",
    # Helper functions
    "generate_random_string",
    # Safe field updater
    "SafeFieldUpdater",
]
