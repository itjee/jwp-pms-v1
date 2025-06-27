"""
Task Pydantic Schemas

Request/Response schemas for task management.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from schemas.user import UserPublic


class TaskBase(BaseModel):
    """Base task schema"""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(
        None, max_length=5000, description="Task description"
    )
    status: str = Field(default="todo", description="Task status")
    priority: str = Field(default="medium", description="Task priority")
    task_type: str = Field(default="feature", description="Task type")

    @validator("status")
    def validate_status(cls, v):
        valid_statuses = [
            "todo",
            "in_progress",
            "in_review",
            "testing",
            "done",
            "blocked",
            "on_hold",
            "cancelled",
        ]
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

    @validator("priority")
    def validate_priority(cls, v):
        valid_priorities = ["low", "medium", "high", "urgent"]
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(valid_priorities)}')
        return v

    @validator("task_type")
    def validate_task_type(cls, v):
        valid_types = [
            "feature",
            "bug",
            "task",
            "enhancement",
            "improvement",
            "refactoring",
            "debt",
            "research",
            "documentation",
            "support",
            "testing",
            "maintenance",
        ]
        if v not in valid_types:
            raise ValueError(f'Task type must be one of: {", ".join(valid_types)}')
        return v


class TaskCreate(TaskBase):
    """Schema for creating a task"""

    project_id: int = Field(..., description="Project ID")
    parent_task_id: Optional[int] = Field(
        None, description="Parent task ID for subtasks"
    )
    start_date: Optional[datetime] = Field(None, description="Task start date")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    estimated_hours: Optional[int] = Field(None, ge=0, description="Estimated hours")
    story_points: Optional[int] = Field(None, ge=0, description="Story points")
    acceptance_criteria: Optional[str] = Field(
        None, max_length=2000, description="Acceptance criteria"
    )
    external_id: Optional[str] = Field(
        None, max_length=100, description="External system ID"
    )
    assignee_ids: Optional[List[int]] = Field(
        default=[], description="List of assignee user IDs"
    )
    tag_ids: Optional[List[int]] = Field(default=[], description="List of tag IDs")

    @validator("due_date")
    def validate_due_date(cls, v, values):
        if (
            v
            and "start_date" in values
            and values["start_date"]
            and v < values["start_date"]
        ):
            raise ValueError("Due date must be after start date")
        return v


class TaskUpdate(BaseModel):
    """Schema for updating a task"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[str] = None
    priority: Optional[str] = None
    task_type: Optional[str] = None
    parent_task_id: Optional[int] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[int] = Field(None, ge=0)
    actual_hours: Optional[int] = Field(None, ge=0)
    story_points: Optional[int] = Field(None, ge=0)
    acceptance_criteria: Optional[str] = Field(None, max_length=2000)
    external_id: Optional[str] = Field(None, max_length=100)

    @validator("status")
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = [
                "todo",
                "in_progress",
                "in_review",
                "testing",
                "done",
                "blocked",
                "on_hold",
                "cancelled",
            ]
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

    @validator("priority")
    def validate_priority(cls, v):
        if v is not None:
            valid_priorities = ["low", "medium", "high", "urgent"]
            if v not in valid_priorities:
                raise ValueError(
                    f'Priority must be one of: {", ".join(valid_priorities)}'
                )
        return v

    @validator("task_type")
    def validate_task_type(cls, v):
        if v is not None:
            valid_types = [
                "feature",
                "bug",
                "task",
                "enhancement",
                "improvement",
                "refactoring",
                "debt",
                "research",
                "documentation",
                "support",
                "testing",
                "maintenance",
            ]
            if v not in valid_types:
                raise ValueError(f'Task type must be one of: {", ".join(valid_types)}')
        return v


class TaskAssignmentResponse(BaseModel):
    """Schema for task assignment response"""

    id: int
    task_id: int
    user_id: int
    assigned_at: datetime
    assigned_by: int
    is_active: bool = True
    user: UserPublic
    assigner: UserPublic

    class Config:
        from_attributes = True


class TaskCommentBase(BaseModel):
    """Base task comment schema"""

    content: str = Field(
        ..., min_length=1, max_length=2000, description="Comment content"
    )


class TaskCommentCreate(TaskCommentBase):
    """Schema for creating task comment"""

    parent_id: Optional[int] = Field(None, description="Parent comment ID for replies")


class TaskCommentUpdate(BaseModel):
    """Schema for updating task comment"""

    content: str = Field(
        ..., min_length=1, max_length=2000, description="Comment content"
    )


class TaskCommentResponse(BaseModel):
    """Schema for task comment response"""

    id: int
    task_id: int
    author_id: int
    parent_id: Optional[int] = None
    content: str
    is_edited: bool = False
    created_at: datetime
    updated_at: datetime
    author: UserPublic
    replies: List["TaskCommentResponse"] = []

    class Config:
        from_attributes = True


class TaskAttachmentResponse(BaseModel):
    """Schema for task attachment response"""

    id: int
    task_id: int
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


class TaskTimeLogBase(BaseModel):
    """Base task time log schema"""

    hours: int = Field(..., gt=0, description="Hours worked")
    description: Optional[str] = Field(
        None, max_length=500, description="Work description"
    )


class TaskTimeLogCreate(TaskTimeLogBase):
    """Schema for creating task time log"""

    work_date: Optional[datetime] = Field(
        None, description="Date of work (default: today)"
    )


class TaskTimeLogUpdate(TaskTimeLogBase):
    """Schema for updating task time log"""

    work_date: Optional[datetime] = None


class TaskTimeLogResponse(BaseModel):
    """Schema for task time log response"""

    id: int
    task_id: int
    user_id: int
    hours: int
    description: Optional[str] = None
    work_date: datetime
    created_at: datetime
    updated_at: datetime
    user: UserPublic

    class Config:
        from_attributes = True


class TagBase(BaseModel):
    """Base tag schema"""

    name: str = Field(..., min_length=1, max_length=50, description="Tag name")
    color: Optional[str] = Field("#3B82F6", max_length=7, description="Tag color (hex)")
    description: Optional[str] = Field(
        None, max_length=200, description="Tag description"
    )

    @validator("color")
    def validate_color(cls, v):
        if v is not None and not v.startswith("#"):
            raise ValueError("Color must be in hex format (e.g., #ff0000)")
        return v


class TagCreate(TagBase):
    """Schema for creating a tag"""

    pass


class TagUpdate(BaseModel):
    """Schema for updating a tag"""

    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, max_length=7)
    description: Optional[str] = Field(None, max_length=200)

    @validator("color")
    def validate_color(cls, v):
        if v is not None and not v.startswith("#"):
            raise ValueError("Color must be in hex format (e.g., #ff0000)")
        return v


class TagResponse(TagBase):
    """Schema for tag response"""

    id: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class TaskResponse(TaskBase):
    """Schema for task response"""

    id: int
    project_id: int
    creator_id: int
    parent_task_id: Optional[int] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    actual_hours: int = 0
    story_points: Optional[int] = None
    acceptance_criteria: Optional[str] = None
    external_id: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    creator: UserPublic
    assignments: List[TaskAssignmentResponse] = []
    comments: List[TaskCommentResponse] = []
    attachments: List[TaskAttachmentResponse] = []
    time_logs: List[TaskTimeLogResponse] = []
    tags: List[TagResponse] = []
    subtasks: List["TaskResponse"] = []

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for task list response"""

    tasks: List[TaskResponse]
    total: int
    page: int
    per_page: int
    pages: int


class TaskStatsResponse(BaseModel):
    """Schema for task statistics"""

    total_tasks: int
    todo_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    overdue_tasks: int
    tasks_by_status: dict
    tasks_by_priority: dict
    tasks_by_type: dict
    average_completion_time: Optional[float] = None


class TaskSearchRequest(BaseModel):
    """Schema for task search request"""

    query: Optional[str] = Field(None, description="Search query")
    project_id: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    task_type: Optional[str] = None
    assignee_id: Optional[int] = None
    creator_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None

    @validator("status")
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = [
                "todo",
                "in_progress",
                "in_review",
                "testing",
                "done",
                "blocked",
                "on_hold",
                "cancelled",
            ]
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

    @validator("priority")
    def validate_priority(cls, v):
        if v is not None:
            valid_priorities = ["low", "medium", "high", "urgent"]
            if v not in valid_priorities:
                raise ValueError(
                    f'Priority must be one of: {", ".join(valid_priorities)}'
                )
        return v

    @validator("task_type")
    def validate_task_type(cls, v):
        if v is not None:
            valid_types = [
                "feature",
                "bug",
                "task",
                "enhancement",
                "improvement",
                "refactoring",
                "debt",
                "research",
                "documentation",
                "support",
                "testing",
                "maintenance",
            ]
            if v not in valid_types:
                raise ValueError(f'Task type must be one of: {", ".join(valid_types)}')
        return v


class TaskAssignRequest(BaseModel):
    """Schema for task assignment request"""

    user_ids: List[int] = Field(..., description="List of user IDs to assign")


class TaskDashboardResponse(BaseModel):
    """Schema for task dashboard response"""

    total_tasks: int
    my_tasks: int
    todo_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    overdue_tasks: int
    recent_tasks: List[TaskResponse]
    my_recent_tasks: List[TaskResponse]
    upcoming_deadlines: List[TaskResponse]
    task_completion_stats: dict


class TaskKanbanBoard(BaseModel):
    """Schema for Kanban board response"""

    todo: List[TaskResponse]
    in_progress: List[TaskResponse]
    in_review: List[TaskResponse]
    testing: List[TaskResponse]
    done: List[TaskResponse]


class TaskGanttChart(BaseModel):
    """Schema for Gantt chart response"""

    task_id: int
    title: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    progress: int = 0
    dependencies: List[int] = []


class TaskGanttResponse(BaseModel):
    """Schema for Gantt chart data response"""

    tasks: List[TaskGanttChart]
    project_start: Optional[datetime]
    project_end: Optional[datetime]


# Update forward references
TaskCommentResponse.model_rebuild()
TaskResponse.model_rebuild()
