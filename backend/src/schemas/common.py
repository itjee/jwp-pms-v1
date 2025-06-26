"""
Common Pydantic Schemas

Shared schemas used across multiple modules.
"""

from datetime import datetime
from typing import Annotated, Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters schema"""

    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: str = Field(default="asc", description="Sort order: asc or desc")

    @validator("sort_order")
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v


class PaginatedResponse(GenericModel, Generic[T]):
    """Generic paginated response schema"""

    items: List[T]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class SearchParams(BaseModel):
    """Search parameters schema"""

    query: Optional[str] = Field(None, description="Search query")
    fields: Optional[List[str]] = Field(None, description="Fields to search in")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")


class SortParams(BaseModel):
    """Sort parameters schema"""

    field: str = Field(..., description="Field to sort by")
    order: str = Field(default="asc", description="Sort order: asc or desc")

    @validator("order")
    def validate_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v


class FilterParams(BaseModel):
    """Filter parameters schema"""

    field: str = Field(..., description="Field to filter by")
    operator: str = Field(..., description="Filter operator")
    value: Any = Field(..., description="Filter value")

    @validator("operator")
    def validate_operator(cls, v):
        valid_operators = [
            "eq",
            "ne",
            "gt",
            "gte",
            "lt",
            "lte",
            "in",
            "not_in",
            "like",
            "ilike",
        ]
        if v not in valid_operators:
            raise ValueError(f'Operator must be one of: {", ".join(valid_operators)}')
        return v


class DateRangeFilter(BaseModel):
    """Date range filter schema"""

    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")

    @validator("end_date")
    def validate_end_date(cls, v, values):
        if (
            v
            and "start_date" in values
            and values["start_date"]
            and v < values["start_date"]
        ):
            raise ValueError("End date must be after start date")
        return v


class SuccessResponse(BaseModel):
    """Success response schema"""

    success: bool = True
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data")


class ErrorResponse(BaseModel):
    """Error response schema"""

    success: bool = False
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationErrorResponse(BaseModel):
    """Validation error response schema"""

    success: bool = False
    error: str = "Validation error"
    details: List[Dict[str, Any]] = Field(..., description="Validation error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FileUploadResponse(BaseModel):
    """File upload response schema"""

    filename: str = Field(..., description="Original filename")
    file_path: str = Field(..., description="File storage path")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: Optional[str] = Field(None, description="MIME type")
    url: str = Field(..., description="File access URL")


class BulkOperationRequest(BaseModel):
    """Bulk operation request schema"""

    ids: List[int] = Field(..., min_items=1, description="List of IDs to operate on")
    operation: str = Field(..., description="Operation to perform")
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Operation parameters"
    )


class BulkOperationResponse(BaseModel):
    """Bulk operation response schema"""

    total: int = Field(..., description="Total items processed")
    successful: int = Field(..., description="Successfully processed items")
    failed: int = Field(..., description="Failed items")
    errors: List[Dict[str, Any]] = Field(default=[], description="Error details")


class HealthCheckResponse(BaseModel):
    """Health check response schema"""

    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Environment name")
    services: Dict[str, str] = Field(default={}, description="Service health status")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional health details"
    )


class SystemInfoResponse(BaseModel):
    """System information response schema"""

    application: Dict[str, Any] = Field(..., description="Application information")
    system: Dict[str, Any] = Field(..., description="System information")
    configuration: Dict[str, Any] = Field(..., description="Configuration status")
    features: Dict[str, bool] = Field(..., description="Feature availability")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StatsResponse(BaseModel):
    """Statistics response schema"""

    total_count: int = Field(..., description="Total items count")
    counts_by_status: Dict[str, int] = Field(default={}, description="Counts by status")
    counts_by_type: Dict[str, int] = Field(default={}, description="Counts by type")
    recent_activity: List[Dict[str, Any]] = Field(
        default=[], description="Recent activity"
    )
    trends: Dict[str, Any] = Field(default={}, description="Trend data")


class ExportRequest(BaseModel):
    """Export request schema"""

    format: str = Field(..., description="Export format: csv, xlsx, json, pdf")
    filters: Optional[Dict[str, Any]] = Field(None, description="Export filters")
    fields: Optional[List[str]] = Field(None, description="Fields to include")

    @validator("format")
    def validate_format(cls, v):
        valid_formats = ["csv", "xlsx", "json", "pdf"]
        if v not in valid_formats:
            raise ValueError(f'Format must be one of: {", ".join(valid_formats)}')
        return v


class ExportResponse(BaseModel):
    """Export response schema"""

    export_id: str = Field(..., description="Export job ID")
    status: str = Field(..., description="Export status")
    download_url: Optional[str] = Field(None, description="Download URL when ready")
    expires_at: Optional[datetime] = Field(None, description="Download expiration")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ImportRequest(BaseModel):
    """Import request schema"""

    file_path: str = Field(..., description="Uploaded file path")
    format: str = Field(..., description="Import format: csv, xlsx, json")
    mapping: Optional[Dict[str, str]] = Field(None, description="Field mapping")
    options: Optional[Dict[str, Any]] = Field(None, description="Import options")

    @validator("format")
    def validate_format(cls, v):
        valid_formats = ["csv", "xlsx", "json"]
        if v not in valid_formats:
            raise ValueError(f'Format must be one of: {", ".join(valid_formats)}')
        return v


class ImportResponse(BaseModel):
    """Import response schema"""

    import_id: str = Field(..., description="Import job ID")
    status: str = Field(..., description="Import status")
    total_records: Optional[int] = Field(None, description="Total records to import")
    processed_records: int = Field(default=0, description="Processed records")
    successful_records: int = Field(
        default=0, description="Successfully imported records"
    )
    failed_records: int = Field(default=0, description="Failed records")
    errors: List[Dict[str, Any]] = Field(default=[], description="Import errors")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")


class NotificationPreferences(BaseModel):
    """Notification preferences schema"""

    email_notifications: bool = Field(
        default=True, description="Enable email notifications"
    )
    push_notifications: bool = Field(
        default=True, description="Enable push notifications"
    )
    task_assigned: bool = Field(default=True, description="Notify when task assigned")
    task_completed: bool = Field(default=True, description="Notify when task completed")
    project_updates: bool = Field(default=True, description="Notify on project updates")
    deadline_reminders: bool = Field(
        default=True, description="Send deadline reminders"
    )
    event_reminders: bool = Field(default=True, description="Send event reminders")


class ActivityLogEntry(BaseModel):
    """Activity log entry schema"""

    id: int
    user_id: Optional[int] = None
    action: str = Field(..., description="Action performed")
    resource_type: Optional[str] = Field(None, description="Resource type")
    resource_id: Optional[int] = Field(None, description="Resource ID")
    details: Optional[Dict[str, Any]] = Field(None, description="Action details")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    timestamp: datetime = Field(..., description="Action timestamp")

    class Config:
        from_attributes = True


class ActivityLogResponse(BaseModel):
    """Activity log response schema"""

    logs: List[ActivityLogEntry]
    total: int
    page: int
    per_page: int
    pages: int


class TimeRange(BaseModel):
    """Time range schema"""

    start: datetime = Field(..., description="Start time")
    end: datetime = Field(..., description="End time")

    @validator("end")
    def validate_end(cls, v, values):
        if "start" in values and v <= values["start"]:
            raise ValueError("End time must be after start time")
        return v


class Coordinates(BaseModel):
    """Geographic coordinates schema"""

    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")


class Address(BaseModel):
    """Address schema"""

    street: Optional[str] = Field(None, max_length=200, description="Street address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=100, description="State/Province")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal code")
    country: Optional[str] = Field(None, max_length=100, description="Country")
    coordinates: Optional[Coordinates] = Field(
        None, description="Geographic coordinates"
    )


class ContactInfo(BaseModel):
    """Contact information schema"""

    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    website: Optional[str] = Field(None, max_length=200, description="Website URL")
    address: Optional[Address] = Field(None, description="Physical address")


class Metadata(BaseModel):
    """Generic metadata schema"""

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: Optional[int] = Field(None, description="Creator user ID")
    updated_by: Optional[int] = Field(None, description="Last updater user ID")
    version: int = Field(default=1, description="Version number")
    tags: List[str] = Field(default=[], description="Associated tags")

    class Config:
        from_attributes = True
