"""
User Models

SQLAlchemy models for user management and authentication.
"""

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.constants import UserRole, UserStatus
from core.database import Base

if TYPE_CHECKING:
    from models.calendar import Calendar, Event
    from models.project import Project, ProjectMember
    from models.task import Task, TaskAssignment


class User(Base):
    """
    User model for authentication and profile management
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, doc="User ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, nullable=True, doc="User who created this record")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(Integer, nullable=True, doc="User who last updated this record")

    # Basic Information
    name = Column(
        String(100), unique=True, index=True, nullable=False, doc="Username (unique)"
    )

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        doc="User email address (unique)",
    )

    full_name = Column(String(200), nullable=True, doc="User's full name")

    # Authentication
    password = Column(String(255), nullable=False, doc="Hashed password")
    is_active = Column(
        Boolean, default=True, nullable=False, doc="Whether the user account is active"
    )
    is_verified = Column(
        Boolean, default=False, nullable=False, doc="Whether the user email is verified"
    )

    # Profile Information
    role = Column(
        String(20),  # SQLEnum(UserRole),
        default=UserRole.DEVELOPER,
        nullable=False,
        doc="User role in the system",
    )
    status = Column(
        String(20),  # SQLEnum(UserStatus),
        default=UserStatus.PENDING,
        nullable=False,
        doc="User account status",
    )
    avatar_url = Column(String(500), nullable=True, doc="URL to user's avatar image")
    bio = Column(Text, nullable=True, doc="User biography")

    # Contact Information
    phone = Column(String(20), nullable=True, doc="Phone number")
    department = Column(String(100), nullable=True, doc="User's department")
    position = Column(String(100), nullable=True, doc="User's job position")

    # OAuth Information
    google_id = Column(String(100), nullable=True, index=True, doc="Google OAuth ID")
    github_id = Column(String(100), nullable=True, index=True, doc="GitHub OAuth ID")

    # Activity Tracking
    last_login = Column(
        DateTime(timezone=True), nullable=True, doc="Last login timestamp"
    )
    last_active = Column(
        DateTime(timezone=True), nullable=True, doc="Last activity timestamp"
    )

    # Relationships
    created_projects = relationship(
        "Project", back_populates="creator", foreign_keys="Project.creator_id"
    )

    project_memberships = relationship("ProjectMember", back_populates="user")

    task_assignments = relationship("TaskAssignment", back_populates="assignee")

    created_tasks = relationship(
        "Task", back_populates="creator", foreign_keys="Task.creator_id"
    )

    calendars = relationship("Calendar", back_populates="owner")

    created_events = relationship(
        "Event", back_populates="creator", foreign_keys="Event.creator_id"
    )

    activity_logs = relationship("UserActivityLog", back_populates="user")

    # Constraints
    __table_args__ = (
        UniqueConstraint("email", name="ux_users_email"),
        UniqueConstraint("name", name="ux_users_name"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"

    def update_last_active(self):
        """Update the last active timestamp to the current time"""
        self.last_active = datetime.utcnow()

    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role in [UserRole.ADMIN]

    def is_manager_or_admin(self) -> bool:
        """Check if user is manager or admin"""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]

    def can_manage_users(self) -> bool:
        """Check if user can manage other users"""
        return self.role in [UserRole.ADMIN]


class UserActivityLog(Base):
    """
    User activity logging model
    """

    __tablename__ = "user_activity_logs"

    id = Column(Integer, primary_key=True, index=True, doc="Log ID")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        doc="Timestamp of the log entry",
    )
    created_by = Column(Integer, nullable=True, doc="User who created this log entry")

    user_id = Column(
        Integer, nullable=False, index=True, doc="User ID who performed the action"
    )

    action = Column(
        String(100),
        nullable=False,
        doc="Action performed (e.g., 'login', 'create_project')",
    )

    resource_type = Column(
        String(50),
        nullable=True,
        doc="Type of resource affected (e.g., 'project', 'task')",
    )

    resource_id = Column(String(50), nullable=True, doc="ID of the affected resource")

    description = Column(Text, nullable=True, doc="Detailed description of the action")

    ip_address = Column(
        String(45), nullable=True, doc="IP address from which action was performed"
    )

    user_agent = Column(String(500), nullable=True, doc="User agent string")

    extra_data = Column(Text, nullable=True, doc="Additional metadata as JSON string")

    # Relationships
    user = relationship("User", back_populates="activity_logs")

    def __repr__(self) -> str:
        return f"<UserActivityLog(id={self.id}, user_id={self.user_id}, action='{self.action}')>"


class UserSession(Base):
    """
    User session management model
    """

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True, doc="Session ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, nullable=True, doc="User who created this session")

    user_id = Column(String(50), nullable=False, index=True, doc="User ID")
    session_token = Column(
        String(255), unique=True, nullable=False, doc="Session token"
    )
    refresh_token = Column(String(255), unique=True, nullable=True, doc="Refresh token")
    expires_at = Column(
        DateTime(timezone=True), nullable=False, doc="Session expiration time"
    )
    is_active = Column(
        Boolean, default=True, nullable=False, doc="Whether the session is active"
    )
    ip_address = Column(String(45), nullable=True, doc="IP address of the session")
    user_agent = Column(String(500), nullable=True, doc="User agent string")

    # Relationships
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"

    def revoke(self):
        """Revoke the session"""
        self.is_active = False
