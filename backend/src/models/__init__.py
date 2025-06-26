"""
Database Models Package

SQLAlchemy models for the PMS application.
"""

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
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base

__all__ = [
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

# Base class for all models
Base = declarative_base(metadata=MetaData())

# Import all models to ensure they are registered with SQLAlchemy
from models import calendar, project, task, user

# Ensure all models are imported to register them with SQLAlchemy
__all__.extend(
    [
        "calendar",
        "project",
        "task",
        "user",
    ]
)
# Register all models with the Base class
Base.registry.mapped_classes.extend(
    [
        User,
        UserRole,
        UserStatus,
        UserActivityLog,
        UserSession,
        Project,
        ProjectStatus,
        ProjectPriority,
        ProjectMember,
        ProjectMemberRole,
        ProjectComment,
        ProjectAttachment,
        Task,
        TaskStatus,
        TaskPriority,
        TaskType,
        TaskAssignment,
        TaskComment,
        TaskAttachment,
        TaskTimeLog,
        Tag,
        TaskTag,
        Calendar,
        Event,
        EventType,
        EventStatus,
        RecurrenceType,
        EventAttendee,
    ]
)
# Ensure all models are registered with the Base class
Base.metadata.create_all(bind=None)  # Replace None with your actual engine if needed

# This will ensure that all models are available for import
# and can be used in the application.
# This is necessary for SQLAlchemy to recognize the models
# and create the necessary tables in the database.
# If you have a specific engine, replace None with your SQLAlchemy engine instance.
# This is typically done in the main application file or a dedicated setup script.
# Note: The `create_all` method is usually called in the application startup
# to ensure that all tables are created in the database.
