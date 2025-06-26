"""
Pydantic Schemas Package

Request/Response schemas for API validation.
"""

# Auth schemas
from .auth import *

# Calendar schemas
from .calendar import *

# Common schemas
from .common import *

# Project schemas
from .project import *

# Task schemas
from .task import *

# User schemas
from .user import *

__all__ = [
    # Auth schemas
    "LoginRequest",
    "LoginResponse",
    "LogoutRequest",
    "PasswordChangeRequest",
    "PasswordResetConfirm",
    "PasswordResetRequest",
    "Token",
    "TokenData",
    "TokenRefresh",
    # Calendar schemas
    "CalendarBase",
    "CalendarCreate",
    "CalendarListResponse",
    "CalendarResponse",
    "CalendarStatsResponse",
    "CalendarUpdate",
    "CalendarViewRequest",
    "EventAttendeeRequest",
    "EventAttendeeResponse",
    "EventAttendeeResponseUpdate",
    "EventBase",
    "EventCreate",
    "EventDashboardResponse",
    "EventListResponse",
    "EventResponse",
    "EventSearchRequest",
    "EventType",
    "EventUpdate",
    "RecurringEventResponse",
    "RecurrenceType",
    # Common schemas
    "ActivityLogEntry",
    "ActivityLogResponse",
    "Address",
    "BulkOperationRequest",
    "BulkOperationResponse",
    "ContactInfo",
    "Coordinates",
    "DateRangeFilter",
    "ErrorResponse",
    "ExportRequest",
    "ExportResponse",
    "FileUploadResponse",
    "FilterParams",
    "HealthCheckResponse",
    "ImportRequest",
    "ImportResponse",
    "Metadata",
    "NotificationPreferences",
    "PaginatedResponse",
    "PaginationParams",
    "SearchParams",
    "SortParams",
    "StatsResponse",
    "SuccessResponse",
    "SystemInfoResponse",
    "TimeRange",
    "ValidationErrorResponse",
    # Project schemas
    "ProjectAttachmentResponse",
    "ProjectBase",
    "ProjectCommentBase",
    "ProjectCommentCreate",
    "ProjectCommentResponse",
    "ProjectCommentUpdate",
    "ProjectCreate",
    "ProjectDashboardResponse",
    "ProjectListResponse",
    "ProjectMemberBase",
    "ProjectMemberCreate",
    "ProjectMemberResponse",
    "ProjectMemberRole",
    "ProjectMemberUpdate",
    "ProjectPriority",
    "ProjectResponse",
    "ProjectSearchRequest",
    "ProjectStatus",
    "ProjectStatsResponse",
    "ProjectUpdate",
    # Task schemas
    "TagBase",
    "TagCreate",
    "TagResponse",
    "TagUpdate",
    "TaskAssignmentResponse",
    "TaskAssignRequest",
    "TaskAttachmentResponse",
    "TaskBase",
    "TaskCommentBase",
    "TaskCommentCreate",
    "TaskCommentResponse",
    "TaskCommentUpdate",
    "TaskCreate",
    "TaskDashboardResponse",
    "TaskGanttChart",
    "TaskGanttResponse",
    "TaskKanbanBoard",
    "TaskListResponse",
    "TaskPriority",
    "TaskResponse",
    "TaskSearchRequest",
    "TaskStatsResponse",
    "TaskStatus",
    "TaskTimeLogBase",
    "TaskTimeLogCreate",
    "TaskTimeLogResponse",
    "TaskTimeLogUpdate",
    "TaskType",
    "TaskUpdate",
    # User schemas
    "UserActivityLogResponse",
    "UserBase",
    "UserCreate",
    "UserEmailVerification",
    "UserListResponse",
    "UserLogin",
    "UserLoginResponse",
    "UserPasswordChange",
    "UserPasswordReset",
    "UserPasswordResetConfirm",
    "UserProfileUpdate",
    "UserPublic",
    "UserRefreshToken",
    "UserResponse",
    "UserRole",
    "UserSessionResponse",
    "UserStatsResponse",
    "UserStatus",
    "UserUpdate",
]
