"""
Project Models

SQLAlchemy models for project management.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.constants import ProjectMemberRole, ProjectPriority, ProjectStatus
from core.database import Base

if TYPE_CHECKING:
    from models.calendar import Event
    from models.task import Task
    from models.user import User


class Project(Base):
    """
    Project model for project management
    """

    __tablename__ = "projects"

    # Unique identifier and timestamps
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Unique identifier for the project",
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Project creation timestamp",
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        doc="User who created the project",
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Project last update timestamp",
    )
    updated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        doc="User who last updated the project",
    )

    # Basic Information
    name = Column(String(200), nullable=False, index=True, doc="Project name")
    description = Column(Text, nullable=True, doc="Project description")

    # Status and Priority
    status = Column(
        String(20),  # Enum(ProjectStatus),
        default=ProjectStatus.PLANNING,
        nullable=False,
        doc="Project status",
    )
    priority = Column(
        String(20),  # Enum(ProjectPriority),
        default=ProjectPriority.MEDIUM,
        nullable=False,
        doc="Project priority",
    )

    # Timeline
    start_date = Column(
        DateTime(timezone=True), nullable=True, doc="Project start date"
    )
    end_date = Column(DateTime(timezone=True), nullable=True, doc="Project end date")
    actual_start_date = Column(
        DateTime(timezone=True), nullable=True, doc="Actual project start date"
    )
    actual_end_date = Column(
        DateTime(timezone=True), nullable=True, doc="Actual project end date"
    )

    # Progress and Budget
    progress = Column(
        Integer, default=0, nullable=False, doc="Project progress percentage (0-100)"
    )
    budget = Column(Numeric(15, 2), nullable=True, doc="Project budget")
    actual_cost = Column(
        Numeric(15, 2),
        default=Decimal("0.00"),
        nullable=False,
        doc="Actual project cost",
    )

    # Ownership and Visibility
    creator_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        doc="User who created the project",
    )
    is_active = Column(
        Boolean, default=True, nullable=False, doc="Whether the project is active"
    )
    is_public = Column(
        Boolean, default=False, nullable=False, doc="Whether the project is public"
    )

    # Additional Information
    repository_url = Column(String(500), nullable=True, doc="Git repository URL")
    documentation_url = Column(String(500), nullable=True, doc="Documentation URL")
    tags = Column(Text, nullable=True, doc="Project tags (comma-separated)")

    # Relationships
    creator = relationship(
        "User", back_populates="created_projects", foreign_keys=[creator_id]
    )

    members = relationship(
        "ProjectMember", back_populates="project", cascade="all, delete-orphan"
    )

    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

    comments = relationship(
        "ProjectComment", back_populates="project", cascade="all, delete-orphan"
    )

    attachments = relationship(
        "ProjectAttachment", back_populates="project", cascade="all, delete-orphan"
    )

    events = relationship("Event", back_populates="project")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "progress >= 0 AND progress <= 100", name="ck_project_progress"
        ),
        CheckConstraint("budget >= 0", name="ck_project_budget_positive"),
        CheckConstraint("actual_cost >= 0", name="ck_project_actual_cost_positive"),
        CheckConstraint("start_date <= end_date", name="ck_project_date_order"),
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"

    def update_progress(self):
        """Update project progress based on completed tasks"""
        if not self.tasks:
            self.progress = 0
            return

        completed_tasks = sum(1 for task in self.tasks if task.status == "completed")
        total_tasks = len(self.tasks)
        self.progress = int((completed_tasks / total_tasks) * 100)


class ProjectMember(Base):
    """
    Project member association model
    """

    __tablename__ = "project_members"

    # Unique identifier and timestamps
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Unique identifier for the project member",
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Project member creation timestamp",
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        doc="User who created the project member association",
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Project member last update timestamp",
    )
    updated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        doc="User who last updated the project member association",
    )

    # Basic Information
    project_id = Column(
        Integer, ForeignKey("projects.id"), nullable=False, doc="Project ID"
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, doc="User ID")
    role = Column(
        String(20),  # Enum(ProjectMemberRole),
        default=ProjectMemberRole.DEVELOPER,
        nullable=False,
        doc="Member role in the project",
    )
    joined_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        doc="When the user joined the project",
    )
    is_active = Column(
        Boolean, default=True, nullable=False, doc="Whether the membership is active"
    )

    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "project_id", "user_id", name="ux_project_members__project_user"
        ),
    )

    def __repr__(self) -> str:
        return f"<ProjectMember(project_id={self.project_id}, user_id={self.user_id}, role='{self.role}')>"

    def can_manage_project(self) -> bool:
        """Check if member can manage the project"""
        return self.role in [ProjectMemberRole.OWNER, ProjectMemberRole.MANAGER]

    def can_assign_tasks(self) -> bool:
        """Check if member can assign tasks"""
        return self.role in [ProjectMemberRole.OWNER, ProjectMemberRole.MANAGER]


class ProjectComment(Base):
    """
    Project comment model
    """

    __tablename__ = "project_comments"

    # Unique identifier and timestamps
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Unique identifier for the project comment",
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Comment creation timestamp",
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        doc="User who created the comment",
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Comment last update timestamp",
    )
    updated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        doc="User who last updated the comment",
    )

    # Basic Information
    project_id = Column(
        Integer, ForeignKey("projects.id"), nullable=False, doc="Project ID"
    )
    author_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, doc="Comment author ID"
    )
    content = Column(Text, nullable=False, doc="Comment content")
    parent_id = Column(
        Integer,
        ForeignKey("project_comments.id"),
        nullable=True,
        doc="Parent comment ID for replies",
    )
    is_edited = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the comment has been edited",
    )

    # Relationships
    project = relationship("Project", back_populates="comments")
    author = relationship("User")
    # parent = relationship("ProjectComment", remote_side=[Base.id])
    parent = relationship(
        "ProjectComment",
        remote_side=lambda: ProjectComment.id,
        back_populates="recurring_instances",
    )
    replies = relationship(
        "ProjectComment", back_populates="parent", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ProjectComment(id={self.id}, project_id={self.project_id}, author_id={self.author_id})>"


class ProjectAttachment(Base):
    """
    Project attachment model
    """

    __tablename__ = "project_attachments"

    # Unique identifier and timestamps
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Unique identifier for the project attachment",
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Attachment creation timestamp",
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        doc="User who created the attachment",
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Attachment last update timestamp",
    )
    updated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        doc="User who last updated the attachment",
    )

    # Basic Information
    project_id = Column(
        Integer, ForeignKey("projects.id"), nullable=False, doc="Project ID"
    )
    filename = Column(String(255), nullable=False, doc="Original filename")
    file_path = Column(String(500), nullable=False, doc="File storage path")
    file_size = Column(Integer, nullable=False, doc="File size in bytes")
    mime_type = Column(String(100), nullable=True, doc="MIME type of the file")
    uploaded_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        doc="User who uploaded the file",
    )
    description = Column(Text, nullable=True, doc="File description")

    # Relationships
    project = relationship("Project", back_populates="attachments")
    uploader = relationship("User")

    def __repr__(self) -> str:
        return f"<ProjectAttachment(id={self.id}, filename='{self.filename}', project_id={self.project_id})>"
