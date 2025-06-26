# backend/src/utils/exceptions.py
"""
Custom Exception Classes

Application-specific exceptions for better error handling and API responses.
"""

from typing import Any, Dict, Optional


class BaseAPIException(Exception):
    """Base exception class for API errors"""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseAPIException):
    """Raised when input validation fails"""

    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class NotFoundError(BaseAPIException):
    """Raised when a requested resource is not found"""

    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[Any] = None,
    ):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id

        super().__init__(
            message=message, status_code=404, error_code="NOT_FOUND", details=details
        )


class ConflictError(BaseAPIException):
    """Raised when a resource conflict occurs"""

    def __init__(
        self,
        message: str = "Resource conflict",
        conflicting_field: Optional[str] = None,
        conflicting_value: Optional[Any] = None,
    ):
        details = {}
        if conflicting_field:
            details["conflicting_field"] = conflicting_field
        if conflicting_value:
            details["conflicting_value"] = str(conflicting_value)

        super().__init__(
            message=message, status_code=409, error_code="CONFLICT", details=details
        )


class AuthenticationError(BaseAPIException):
    """Raised when authentication fails"""

    def __init__(
        self, message: str = "Authentication failed", auth_type: Optional[str] = None
    ):
        details = {}
        if auth_type:
            details["auth_type"] = auth_type

        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationError(BaseAPIException):
    """Raised when authorization fails"""

    def __init__(
        self,
        message: str = "Access denied",
        required_permission: Optional[str] = None,
        user_role: Optional[str] = None,
    ):
        details = {}
        if required_permission:
            details["required_permission"] = required_permission
        if user_role:
            details["user_role"] = user_role

        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details,
        )


class BusinessLogicError(BaseAPIException):
    """Raised when business logic rules are violated"""

    def __init__(
        self, message: str = "Business logic error", rule: Optional[str] = None
    ):
        details = {}
        if rule:
            details["rule"] = rule

        super().__init__(
            message=message,
            status_code=422,
            error_code="BUSINESS_LOGIC_ERROR",
            details=details,
        )


class ExternalServiceError(BaseAPIException):
    """Raised when external service calls fail"""

    def __init__(
        self,
        message: str = "External service error",
        service_name: Optional[str] = None,
        service_error: Optional[str] = None,
    ):
        details = {}
        if service_name:
            details["service_name"] = service_name
        if service_error:
            details["service_error"] = service_error

        super().__init__(
            message=message,
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
        )


class DatabaseError(BaseAPIException):
    """Raised when database operations fail"""

    def __init__(
        self,
        message: str = "Database error",
        operation: Optional[str] = None,
        table: Optional[str] = None,
    ):
        details = {}
        if operation:
            details["operation"] = operation
        if table:
            details["table"] = table

        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details=details,
        )


class FileUploadError(BaseAPIException):
    """Raised when file upload operations fail"""

    def __init__(
        self,
        message: str = "File upload error",
        filename: Optional[str] = None,
        file_size: Optional[int] = None,
        max_size: Optional[int] = None,
    ):
        details = {}
        if filename:
            details["filename"] = filename
        if file_size:
            details["file_size"] = file_size
        if max_size:
            details["max_size"] = max_size

        super().__init__(
            message=message,
            status_code=413,
            error_code="FILE_UPLOAD_ERROR",
            details=details,
        )


class RateLimitError(BaseAPIException):
    """Raised when rate limits are exceeded"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: Optional[int] = None,
        reset_time: Optional[int] = None,
    ):
        details = {}
        if limit:
            details["limit"] = limit
        if reset_time:
            details["reset_time"] = reset_time

        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_ERROR",
            details=details,
        )


class ConfigurationError(BaseAPIException):
    """Raised when configuration is invalid or missing"""

    def __init__(
        self, message: str = "Configuration error", config_key: Optional[str] = None
    ):
        details = {}
        if config_key:
            details["config_key"] = config_key

        super().__init__(
            message=message,
            status_code=500,
            error_code="CONFIGURATION_ERROR",
            details=details,
        )


class PermissionDeniedError(AuthorizationError):
    """Raised when specific permissions are denied"""

    def __init__(
        self,
        message: str = "Permission denied",
        resource: Optional[str] = None,
        action: Optional[str] = None,
    ):
        details = {}
        if resource:
            details["resource"] = resource
        if action:
            details["action"] = action

        super().__init__(
            message=message,
            required_permission=f"{resource}:{action}" if resource and action else None,
        )


class UserNotActiveError(AuthenticationError):
    """Raised when user account is not active"""

    def __init__(
        self,
        message: str = "User account is not active",
        user_status: Optional[str] = None,
    ):
        details = {}
        if user_status:
            details["user_status"] = user_status

        super().__init__(message=message, auth_type="user_status")


class TokenExpiredError(AuthenticationError):
    """Raised when authentication token has expired"""

    def __init__(
        self, message: str = "Token has expired", token_type: Optional[str] = None
    ):
        details = {}
        if token_type:
            details["token_type"] = token_type

        super().__init__(message=message, auth_type="token_expired")


class InvalidTokenError(AuthenticationError):
    """Raised when authentication token is invalid"""

    def __init__(
        self, message: str = "Invalid token", token_type: Optional[str] = None
    ):
        details = {}
        if token_type:
            details["token_type"] = token_type

        super().__init__(message=message, auth_type="invalid_token")


class ProjectAccessDeniedError(AuthorizationError):
    """Raised when project access is denied"""

    def __init__(
        self,
        message: str = "Project access denied",
        project_id: Optional[int] = None,
        required_role: Optional[str] = None,
    ):
        details = {}
        if project_id:
            details["project_id"] = project_id
        if required_role:
            details["required_role"] = required_role

        super().__init__(message=message, required_permission="project_access")


class TaskAccessDeniedError(AuthorizationError):
    """Raised when task access is denied"""

    def __init__(
        self,
        message: str = "Task access denied",
        task_id: Optional[int] = None,
        required_permission: Optional[str] = None,
    ):
        details = {}
        if task_id:
            details["task_id"] = task_id
        if required_permission:
            details["required_permission"] = required_permission

        super().__init__(message=message, required_permission=required_permission)


class EmailSendError(ExternalServiceError):
    """Raised when email sending fails"""

    def __init__(
        self,
        message: str = "Failed to send email",
        recipient: Optional[str] = None,
        email_type: Optional[str] = None,
    ):
        details = {}
        if recipient:
            details["recipient"] = recipient
        if email_type:
            details["email_type"] = email_type

        super().__init__(message=message, service_name="email_service")


class DuplicateResourceError(ConflictError):
    """Raised when trying to create a duplicate resource"""

    def __init__(
        self,
        message: str = "Resource already exists",
        resource_type: Optional[str] = None,
        identifier: Optional[str] = None,
    ):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if identifier:
            details["identifier"] = identifier

        super().__init__(message=message, conflicting_field=identifier)


class InvalidOperationError(BusinessLogicError):
    """Raised when an invalid operation is attempted"""

    def __init__(
        self,
        message: str = "Invalid operation",
        operation: Optional[str] = None,
        reason: Optional[str] = None,
    ):
        details = {}
        if operation:
            details["operation"] = operation
        if reason:
            details["reason"] = reason

        super().__init__(
            message=message,
            rule=f"invalid_operation_{operation}" if operation else "invalid_operation",
        )


class ResourceLimitExceededError(BusinessLogicError):
    """Raised when resource limits are exceeded"""

    def __init__(
        self,
        message: str = "Resource limit exceeded",
        resource_type: Optional[str] = None,
        current_count: Optional[int] = None,
        max_limit: Optional[int] = None,
    ):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if current_count:
            details["current_count"] = current_count
        if max_limit:
            details["max_limit"] = max_limit

        super().__init__(
            message=message,
            rule=(
                f"resource_limit_{resource_type}" if resource_type else "resource_limit"
            ),
        )
