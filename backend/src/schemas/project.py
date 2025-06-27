"""
Project Pydantic Schemas

Request/Response schemas for project management.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from core.constants import ProjectPriority, ProjectStatus
from schemas.user import UserPublic


class ProjectBase(BaseModel):
    """Base project schema"""

    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    description: Optional[str] = Field(
        None, max_length=2000, description="Project description"
    )
    status: str = Field(default=ProjectStatus.PLANNING, description="Project status")
    priority: str = Field(
        default=ProjectPriority.MEDIUM, description="Project priority"
    )

    @validator("status")
    def validate_status(cls, v):
        valid_statuses = ["planning", "active", "on_hold", "completed", "cancelled"]
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

    @validator("priority")
    def validate_priority(cls, v):
        valid_priorities = ["low", "medium", "high", "critical"]
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(valid_priorities)}')
        return v


class ProjectCreate(ProjectBase):
    """Schema for creating a project"""

    start_date: Optional[datetime] = Field(None, description="Project start date")
    end_date: Optional[datetime] = Field(None, description="Project end date")
    budget: Optional[Decimal] = Field(None, ge=0, description="Project budget")
    repository_url: Optional[str] = Field(
        None, max_length=500, description="Git repository URL"
    )
    documentation_url: Optional[str] = Field(
        None, max_length=500, description="Documentation URL"
    )
    tags: Optional[str] = Field(
        None, max_length=500, description="Project tags (comma-separated)"
    )
    is_public: bool = Field(default=False, description="Whether the project is public")

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


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[str] = None
    priority: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[Decimal] = Field(None, ge=0)
    actual_cost: Optional[Decimal] = Field(None, ge=0)
    progress: Optional[int] = Field(None, ge=0, le=100)
    repository_url: Optional[str] = Field(None, max_length=500)
    documentation_url: Optional[str] = Field(None, max_length=500)
    tags: Optional[str] = Field(None, max_length=500)
    is_public: Optional[bool] = None

    @validator("status")
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ["planning", "active", "on_hold", "completed", "cancelled"]
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

    @validator("priority")
    def validate_priority(cls, v):
        if v is not None:
            valid_priorities = ["low", "medium", "high", "critical"]
            if v not in valid_priorities:
                raise ValueError(
                    f'Priority must be one of: {", ".join(valid_priorities)}'
                )
        return v


class ProjectMemberBase(BaseModel):
    """Base project member schema"""

    user_id: int = Field(..., description="User ID")
    role: str = Field(default="developer", description="Member role")

    @validator("role")
    def validate_role(cls, v):
        valid_roles = ["owner", "manager", "developer", "reviewer", "viewer"]
        if v not in valid_roles:
            raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v


class ProjectMemberCreate(ProjectMemberBase):
    """Schema for adding project member"""

    pass


class ProjectMemberUpdate(BaseModel):
    """Schema for updating project member"""

    role: str = Field(..., description="Member role")

    @validator("role")
    def validate_role(cls, v):
        valid_roles = ["owner", "manager", "developer", "reviewer", "viewer"]
        if v not in valid_roles:
            raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v


class ProjectMemberResponse(BaseModel):
    """Schema for project member response"""

    id: int
    project_id: int
    user_id: int
    role: str
    joined_at: datetime
    user: UserPublic

    class Config:
        from_attributes = True


class ProjectCommentBase(BaseModel):
    """Base project comment schema"""

    content: str = Field(
        ..., min_length=1, max_length=2000, description="Comment content"
    )


class ProjectCommentCreate(ProjectCommentBase):
    """Schema for creating project comment"""

    parent_id: Optional[int] = Field(None, description="Parent comment ID for replies")


class ProjectCommentUpdate(BaseModel):
    """Schema for updating project comment"""

    content: str = Field(
        ..., min_length=1, max_length=2000, description="Comment content"
    )


class ProjectCommentResponse(BaseModel):
    """Schema for project comment response"""

    id: int
    project_id: int
    author_id: int
    parent_id: Optional[int] = None
    content: str
    created_at: datetime
    updated_at: datetime
    author: UserPublic
    replies: List["ProjectCommentResponse"] = []

    class Config:
        from_attributes = True


class ProjectAttachmentResponse(BaseModel):
    """Schema for project attachment response"""

    id: int
    project_id: int
    filename: str
    file_path: str
    file_size: int
    mime_type: Optional[str] = None
    description: Optional[str] = None
    uploaded_by: int
    created_at: datetime
    uploader: UserPublic

    class Config:
        from_attributes = True


class ProjectResponse(ProjectBase):
    """Schema for project response"""

    id: int
    creator_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    progress: int = 0
    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None
    tags: Optional[str] = None
    is_public: bool = False
    created_at: datetime
    updated_at: datetime
    creator: UserPublic
    members: List[ProjectMemberResponse] = []
    comments: List[ProjectCommentResponse] = []
    attachments: List[ProjectAttachmentResponse] = []

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Schema for project list response"""

    projects: List[ProjectResponse]
    total: int
    page: int
    per_page: int
    pages: int


class ProjectStatsResponse(BaseModel):
    """Schema for project statistics"""

    total_projects: int
    active_projects: int
    completed_projects: int
    projects_by_status: dict
    projects_by_priority: dict
    average_progress: float


class ProjectSearchRequest(BaseModel):
    """Schema for project search request"""

    query: Optional[str] = Field(None, description="Search query")
    status: Optional[str] = None
    priority: Optional[str] = None
    creator_id: Optional[int] = None
    tags: Optional[List[str]] = None
    start_date_from: Optional[datetime] = None
    start_date_to: Optional[datetime] = None
    end_date_from: Optional[datetime] = None
    end_date_to: Optional[datetime] = None
    is_public: Optional[bool] = None

    @validator("status")
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ["planning", "active", "on_hold", "completed", "cancelled"]
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

    @validator("priority")
    def validate_priority(cls, v):
        if v is not None:
            valid_priorities = ["low", "medium", "high", "critical"]
            if v not in valid_priorities:
                raise ValueError(
                    f'Priority must be one of: {", ".join(valid_priorities)}'
                )
        return v


class ProjectDashboardResponse(BaseModel):
    """Schema for project dashboard response"""

    total_projects: int
    active_projects: int
    completed_projects: int
    overdue_projects: int
    recent_projects: List[ProjectResponse]
    my_projects: List[ProjectResponse]
    project_progress_stats: dict
    upcoming_deadlines: List[ProjectResponse]


# Update forward references
ProjectCommentResponse.model_rebuild()
