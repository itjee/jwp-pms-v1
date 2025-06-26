# backend/src/models/__init__.py
"""
Database Models Package

SQLAlchemy models for the PMS application.
"""

# Import Base from database configuration
from core.database import Base

# Calendar models
from models.calendar import (
    Calendar,
    Event,
    EventAttendee,
    EventStatus,
    EventType,
    RecurrenceType,
)

# Project models
from models.project import (
    Project,
    ProjectAttachment,
    ProjectComment,
    ProjectMember,
    ProjectMemberRole,
    ProjectPriority,
    ProjectStatus,
)

# Task models
from models.task import (
    Tag,
    Task,
    TaskAssignment,
    TaskAttachment,
    TaskComment,
    TaskPriority,
    TaskStatus,
    TaskTag,
    TaskTimeLog,
    TaskType,
)

# User models
from models.user import User, UserActivityLog, UserRole, UserSession, UserStatus

__all__ = [
    # Base class
    "Base",
    # User models
    "User",
    "UserRole",
    "UserStatus",
    "UserActivityLog",
    "UserSession",
    # Project models
    "Project",
    "ProjectStatus",
    "ProjectPriority",
    "ProjectMember",
    "ProjectMemberRole",
    "ProjectComment",
    "ProjectAttachment",
    # Task models
    "Task",
    "TaskStatus",
    "TaskPriority",
    "TaskType",
    "TaskAssignment",
    "TaskComment",
    "TaskAttachment",
    "TaskTimeLog",
    "Tag",
    "TaskTag",
    # Calendar models
    "Calendar",
    "Event",
    "EventType",
    "EventStatus",
    "RecurrenceType",
    "EventAttendee",
]
