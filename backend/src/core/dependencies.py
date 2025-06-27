"""
FastAPI Dependencies

Common dependencies for authentication, database, and permissions.
"""

import logging
from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_async_session
from core.security import TokenData, decode_access_token
from models.user import User, UserRole

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_async_session),
) -> Optional[User]:
    """
    Get current user from JWT token
    """
    if not credentials:
        return None

    try:
        # Decode JWT token
        token_data: TokenData = decode_access_token(credentials.credentials)

        if token_data.sub is None:
            raise ValueError("Token data is missing 'sub' claim")

        # Get user from database
        result = await db.execute(select(User).where(User.id == int(token_data.sub)))
        user = result.scalar_one_or_none()

        if not user:
            logger.warning(f"User not found for token subject: {token_data.sub}")
            return None

        if not isinstance(user.is_active, bool) or not user.is_active:
            logger.warning(f"Inactive user attempted access: {user.id}")
            return None

        # Update last active timestamp
        user.update_last_active()
        await db.commit()

        return user

    except Exception as e:
        logger.warning(f"Token validation failed: {e}")
        return None


async def get_current_active_user(
    current_user: Optional[User] = Depends(get_current_user),
) -> User:
    """
    Get current active user (raises exception if not authenticated)
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user and verify admin role
    """
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return current_user


async def get_current_manager_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user and verify manager role or higher
    """
    if not current_user.is_manager():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Manager permissions required"
        )

    return current_user


def require_roles(*roles: UserRole):
    """
    Dependency factory for role-based access control
    """

    async def check_roles(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in roles]}",
            )
        return current_user

    return check_roles


class Pagination:
    """
    Pagination dependency
    """

    def __init__(
        self,
        page: int = 1,
        size: int = settings.DEFAULT_PAGE_SIZE,
        max_size: int = settings.MAX_PAGE_SIZE,
    ):
        if page < 1:
            page = 1
        if size < 1:
            size = settings.DEFAULT_PAGE_SIZE
        if size > max_size:
            size = max_size

        self.page = page
        self.size = size
        self.offset = (page - 1) * size

    @property
    def limit(self) -> int:
        return self.size


def get_pagination(page: int = 1, size: int = settings.DEFAULT_PAGE_SIZE) -> Pagination:
    """
    Get pagination parameters
    """
    return Pagination(page=page, size=size)


class ProjectPermission:
    """
    Project-level permission checker
    """

    @staticmethod
    async def check_project_access(
        project_id: int,
        current_user: User,
        db: AsyncSession,
        required_actions: list | None = None,
    ) -> bool:
        """
        Check if user has access to a project
        """
        from src.models.project import Project, ProjectMember

        # Admin can access everything
        if current_user.is_admin():
            return True

        # Check if user is project creator
        project_result = await db.execute(
            select(Project).where(
                Project.id == project_id, Project.creator_id == current_user.id
            )
        )
        if project_result.scalar_one_or_none():
            return True

        # Check if user is project member
        member_result = await db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == current_user.id,
                ProjectMember.is_active == True,
            )
        )
        return member_result.scalar_one_or_none() is not None


async def get_project_member(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
) -> User:
    """
    Verify user is a member of the specified project
    """
    has_access = await ProjectPermission.check_project_access(
        project_id, current_user, db
    )

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this project",
        )

    return current_user


class TaskPermission:
    """
    Task-level permission checker
    """

    @staticmethod
    async def check_task_access(
        task_id: int, current_user: User, db: AsyncSession
    ) -> bool:
        """
        Check if user has access to a task
        """
        from src.models.task import Task, TaskAssignment

        # Admin can access everything
        if current_user.is_admin():
            return True

        # Get task with project info
        task_result = await db.execute(select(Task).where(Task.id == task_id))
        task = task_result.scalar_one_or_none()

        if not task:
            return False

            # Check if user is task creator

        if task.creator_id is None:
            return False

        creator_id = getattr(task, "creator_id", None)

        if creator_id is not None and int(creator_id) == current_user.id:
            return True

        # Check if user is assigned to the task
        assignment_result = await db.execute(
            select(TaskAssignment).where(
                TaskAssignment.task_id == task_id,
                TaskAssignment.user_id == current_user.id,
                TaskAssignment.is_active == True,
            )
        )
        if assignment_result.scalar_one_or_none():
            return True

        if task.project_id is None:
            # If task has no project, user can access if they are creator
            return False

        project_id = getattr(task, "project_id", None)  # Check project access
        if project_id is None:
            return False

        return await ProjectPermission.check_project_access(
            int(project_id), current_user, db
        )


async def get_task_member(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
) -> User:
    """
    Verify user has access to the specified task
    """
    has_access = await TaskPermission.check_task_access(task_id, current_user, db)

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this task"
        )

    return current_user


class CommonDependencies:
    """
    Common dependency combinations
    """

    @staticmethod
    def paginated_response(
        pagination: Pagination = Depends(get_pagination),
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_async_session),
    ):
        """
        Common dependencies for paginated endpoints
        """
        return {"pagination": pagination, "current_user": current_user, "db": db}

    @staticmethod
    def authenticated_request(
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_async_session),
    ):
        """
        Common dependencies for authenticated endpoints
        """
        return {"current_user": current_user, "db": db}


# Rate limiting (placeholder for future implementation)
class RateLimit:
    """
    Rate limiting dependency (placeholder)
    """

    def __init__(self, calls: int = 100, period: int = 60):
        self.calls = calls
        self.period = period

    async def __call__(self, request):
        # TODO: Implement rate limiting logic
        # For now, just pass through
        return True


def rate_limit(calls: int = 100, period: int = 60):
    """
    Rate limiting dependency factory
    """
    return RateLimit(calls=calls, period=period)
