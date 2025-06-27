# backend/src/services/task.py
"""
Task Service

Business logic for task management operations.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, cast

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import get_async_session
from models.project import Project, ProjectMember
from models.task import (
    Tag,
    Task,
    TaskAssignment,
    TaskAttachment,
    TaskComment,
    TaskTag,
    TaskTimeLog,
)
from models.user import User
from schemas.task import (
    TaskCreate,
    TaskDashboardResponse,
    TaskGanttResponse,
    TaskKanbanBoard,
    TaskListResponse,
    TaskResponse,
    TaskSearchRequest,
    TaskStatsResponse,
    TaskUpdate,
)
from utils.exceptions import (
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)

logger = logging.getLogger(__name__)


class TaskService:
    """Task management service"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_task(self, task_data: TaskCreate, creator_id: int) -> TaskResponse:
        """Create a new task"""
        try:
            # Verify project exists and user has access
            project_result = await self.db.execute(
                select(Project).where(Project.id == task_data.project_id)
            )
            project = project_result.scalar_one_or_none()
            if not project:
                raise NotFoundError(f"Project with ID {task_data.project_id} not found")

            # Check if user has permission to create tasks in this project
            has_access = await self._check_project_access(
                task_data.project_id, creator_id
            )
            if not has_access:
                raise AuthorizationError(
                    "No permission to create tasks in this project"
                )

            # Verify parent task if specified
            if task_data.parent_task_id:
                parent_result = await self.db.execute(
                    select(Task).where(Task.id == task_data.parent_task_id)
                )
                parent_task = parent_result.scalar_one_or_none()

                if not parent_task:
                    raise NotFoundError("Parent task not found")

                parent_project_id = getattr(parent_task, "project_id", None)
                if not parent_project_id:
                    raise ValidationError("Parent task does not belong to any project")

                if parent_project_id != task_data.project_id:
                    raise ValidationError("Parent task must be in the same project")

            # Create task
            task = Task(
                title=task_data.title,
                description=task_data.description,
                status=task_data.status,
                priority=task_data.priority,
                task_type=task_data.task_type,
                project_id=task_data.project_id,
                parent_task_id=task_data.parent_task_id,
                start_date=task_data.start_date,
                due_date=task_data.due_date,
                estimated_hours=task_data.estimated_hours,
                story_points=task_data.story_points,
                acceptance_criteria=task_data.acceptance_criteria,
                external_id=task_data.external_id,
                creator_id=creator_id,
                created_by=creator_id,
                updated_by=creator_id,
            )

            self.db.add(task)
            await self.db.flush()

            # Assign users if specified
            task_id = getattr(task, "id", None)
            if not task_id:
                raise ConflictError("Failed to create task, ID not assigned")

            if task_data.assignee_ids:
                for user_id in task_data.assignee_ids:
                    await self._assign_user_to_task(task_id, user_id, creator_id)

            # Add tags if specified
            if task_data.tag_ids:
                for tag_id in task_data.tag_ids:
                    task_tag = TaskTag(
                        task_id=task.id, tag_id=tag_id, created_by=creator_id
                    )
                    self.db.add(task_tag)

            await self.db.commit()

            # Fetch created task with relationships
            result = await self.db.execute(
                select(Task)
                .options(
                    selectinload(Task.creator),
                    selectinload(Task.assignments).selectinload(TaskAssignment.user),
                    selectinload(Task.tags).selectinload(TaskTag.tag),
                )
                .where(Task.id == task.id)
            )
            created_task = result.scalar_one()

            logger.info(f"Task created successfully: {task.title}")
            return TaskResponse.from_orm(created_task)

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create task: {e}")
            raise

    async def get_task_by_id(
        self, task_id: int, user_id: Optional[int] = None
    ) -> TaskResponse:
        """Get task by ID"""
        try:
            # Build query with relationships
            query = (
                select(Task)
                .options(
                    selectinload(Task.creator),
                    selectinload(Task.project),
                    selectinload(Task.assignments).selectinload(TaskAssignment.user),
                    selectinload(Task.comments).selectinload(TaskComment.author),
                    selectinload(Task.attachments).selectinload(
                        TaskAttachment.uploader
                    ),
                    selectinload(Task.time_logs).selectinload(TaskTimeLog.user),
                    selectinload(Task.tags).selectinload(TaskTag.tag),
                    selectinload(Task.subtasks),
                )
                .where(Task.id == task_id)
            )

            result = await self.db.execute(query)
            task = result.scalar_one_or_none()

            if not task:
                raise NotFoundError(f"Task with ID {task_id} not found")

            # Check access permissions
            if user_id:
                has_access = await self._check_task_access(task_id, user_id)
                if not has_access:
                    raise AuthorizationError("Access denied to this task")

            return TaskResponse.from_orm(task)

        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            raise

    async def update_task(
        self, task_id: int, task_data: TaskUpdate, user_id: int
    ) -> TaskResponse:
        """Update task information"""
        try:
            # Check user has permission to update task
            has_access = await self._check_task_access(task_id, user_id)
            if not has_access:
                raise AuthorizationError("No permission to update this task")

            result = await self.db.execute(select(Task).where(Task.id == task_id))
            task = result.scalar_one_or_none()

            if not task:
                raise NotFoundError(f"Task with ID {task_id} not found")

            # Update fields
            update_data = task_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(task, field, value)

            # Mark as completed if status changed to done
            task_status = getattr(task, "status", None)
            if task_status is None:
                raise ValidationError("Task status cannot be None")

            task_completed_at = getattr(task, "completed_at", None)

            if task_data.status == "done" and task_status != "done":
                setattr(
                    task, "completed_at", datetime.utcnow()
                )  # task.completed_at = datetime.utcnow()
            elif task_data.status != "done" and task_completed_at is not None:
                setattr(task, "completed_at", None)  # task.completed_at = None

            # task.updated_by = user_id
            # task.updated_at = datetime.utcnow()

            setattr(task, "updated_by", user_id)
            setattr(task, "updated_at", datetime.utcnow())

            await self.db.commit()

            # Fetch updated task with relationships
            result = await self.db.execute(
                select(Task)
                .options(
                    selectinload(Task.creator),
                    selectinload(Task.assignments).selectinload(TaskAssignment.user),
                )
                .where(Task.id == task_id)
            )
            updated_task = result.scalar_one()

            logger.info(f"Task updated successfully: {task.title}")
            return TaskResponse.from_orm(updated_task)

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update task {task_id}: {e}")
            raise

    async def delete_task(self, task_id: int, user_id: int) -> bool:
        """Delete task (soft delete)"""
        try:
            # Check user has permission to delete task
            has_access = await self._check_task_access(task_id, user_id)
            if not has_access:
                raise AuthorizationError("No permission to delete this task")

            result = await self.db.execute(select(Task).where(Task.id == task_id))
            task = result.scalar_one_or_none()

            if not task:
                raise NotFoundError(f"Task with ID {task_id} not found")

            # Soft delete by changing status
            setattr(task, "status", "cancelled")  #  task.status = "cancelled"
            setattr(task, "updated_by", user_id)  #  task.updated_by = user_id
            setattr(
                task, "updated_at", datetime.utcnow()
            )  #  task.updated_at = datetime.utcnow()

            await self.db.commit()

            logger.info(f"Task deleted: {task.title}")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete task {task_id}: {e}")
            raise

    async def list_tasks(
        self,
        page: int = 1,
        per_page: int = 20,
        user_id: Optional[int] = None,
        search_params: Optional[TaskSearchRequest] = None,
    ) -> TaskListResponse:
        """List tasks with pagination and filters"""
        try:
            # Build base query
            query = select(Task).options(
                selectinload(Task.creator),
                selectinload(Task.project),
                selectinload(Task.assignments).selectinload(TaskAssignment.user),
            )

            # Apply access control - user can see tasks in projects they have access to
            if user_id:
                accessible_projects = await self._get_accessible_projects(user_id)
                query = query.where(Task.project_id.in_(accessible_projects))

            # Apply search filters
            if search_params:
                if search_params.query:
                    query = query.where(
                        or_(
                            Task.title.ilike(f"%{search_params.query}%"),
                            Task.description.ilike(f"%{search_params.query}%"),
                        )
                    )

                if search_params.project_id:
                    query = query.where(Task.project_id == search_params.project_id)

                if search_params.status:
                    query = query.where(Task.status == search_params.status)

                if search_params.priority:
                    query = query.where(Task.priority == search_params.priority)

                if search_params.task_type:
                    query = query.where(Task.task_type == search_params.task_type)

                if search_params.assignee_id:
                    assignment_subquery = (
                        select(TaskAssignment.task_id)
                        .where(TaskAssignment.user_id == search_params.assignee_id)
                        .where(TaskAssignment.is_active == True)
                    )
                    query = query.where(Task.id.in_(assignment_subquery))

                if search_params.creator_id:
                    query = query.where(Task.creator_id == search_params.creator_id)

                if search_params.due_date_from:
                    query = query.where(Task.due_date >= search_params.due_date_from)

                if search_params.due_date_to:
                    query = query.where(Task.due_date <= search_params.due_date_to)

                if search_params.created_from:
                    query = query.where(Task.created_at >= search_params.created_from)

                if search_params.created_to:
                    query = query.where(Task.created_at <= search_params.created_to)

            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()

            # Apply pagination and ordering
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page).order_by(desc(Task.created_at))

            # Execute query
            result = await self.db.execute(query)
            tasks = result.scalars().all()

            # Calculate pagination info
            pages = ((total if total is not None else 0) + per_page - 1) // per_page

            return TaskListResponse(
                tasks=[TaskResponse.from_orm(task) for task in tasks],
                total=total if total is not None else 0,
                page=page,
                per_page=per_page,
                pages=pages,
            )

        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            raise

    async def assign_task(
        self, task_id: int, user_ids: List[int], assigned_by: int
    ) -> bool:
        """Assign task to users"""
        try:
            # Check permission
            has_access = await self._check_task_access(task_id, assigned_by)
            if not has_access:
                raise AuthorizationError("No permission to assign this task")

            # Verify task exists
            task_result = await self.db.execute(select(Task).where(Task.id == task_id))
            task = task_result.scalar_one_or_none()
            if not task:
                raise NotFoundError("Task not found")

            # Remove existing assignments
            await self.db.execute(
                TaskAssignment.__table__.update()
                .where(TaskAssignment.task_id == task_id)
                .values(is_active=False)
            )

            # Add new assignments
            for user_id in user_ids:
                await self._assign_user_to_task(task_id, user_id, assigned_by)

            await self.db.commit()

            logger.info(f"Task {task_id} assigned to users: {user_ids}")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to assign task {task_id}: {e}")
            raise

    async def get_task_stats(self, user_id: Optional[int] = None) -> TaskStatsResponse:
        """Get task statistics"""
        try:
            # Build base query with access control
            base_query = select(Task)
            if user_id:
                accessible_projects = await self._get_accessible_projects(user_id)
                base_query = base_query.where(Task.project_id.in_(accessible_projects))

            # Total tasks
            total_result = await self.db.execute(
                select(func.count()).select_from(base_query.subquery())
            )
            total_tasks = total_result.scalar()

            # Tasks by status
            status_counts = {}
            for status in ["todo", "in_progress", "done", "blocked", "cancelled"]:
                status_result = await self.db.execute(
                    select(func.count()).select_from(
                        base_query.where(Task.status.value == status).subquery()
                    )
                )
                status_counts[status] = status_result.scalar()

            # Overdue tasks
            overdue_result = await self.db.execute(
                select(func.count()).select_from(
                    base_query.where(
                        and_(
                            Task.due_date < datetime.utcnow(),
                            Task.status.notin_(["done", "cancelled"]),
                        )
                    ).subquery()
                )
            )
            overdue_tasks = overdue_result.scalar()

            # Tasks by priority
            priority_result = await self.db.execute(
                select(Task.priority, func.count(Task.id))
                .select_from(base_query.subquery())
                .group_by(Task.priority)
            )
            # tasks_by_priority = dict(priority_result.fetchall())
            tasks_by_priority = {row[0]: row[1] for row in priority_result.fetchall()}

            # Tasks by type
            type_result = await self.db.execute(
                select(Task.task_type, func.count(Task.id))
                .select_from(base_query.subquery())
                .group_by(Task.task_type)
            )
            # tasks_by_type = dict(type_result.fetchall())
            tasks_by_type = {row[0]: row[1] for row in type_result.fetchall()}

            return TaskStatsResponse(
                total_tasks=total_tasks if total_tasks is not None else 0,
                todo_tasks=status_counts.get("todo", 0),
                in_progress_tasks=status_counts.get("in_progress", 0),
                completed_tasks=status_counts.get("done", 0),
                overdue_tasks=overdue_tasks if overdue_tasks is not None else 0,
                tasks_by_status=status_counts,
                tasks_by_priority=tasks_by_priority,
                tasks_by_type=tasks_by_type,
            )

        except Exception as e:
            logger.error(f"Failed to get task stats: {e}")
            raise

    async def get_kanban_board(
        self, project_id: Optional[int] = None, user_id: Optional[int] = None
    ) -> TaskKanbanBoard:
        """Get tasks organized in Kanban board format"""
        try:
            # Build base query
            query = select(Task).options(
                selectinload(Task.creator),
                selectinload(Task.assignments).selectinload(TaskAssignment.user),
            )

            # Filter by project if specified
            if project_id:
                # Check access to project
                if user_id:
                    has_access = await self._check_project_access(project_id, user_id)
                    if not has_access:
                        raise AuthorizationError("No access to this project")
                query = query.where(Task.project_id == project_id)
            elif user_id:
                # Show tasks from accessible projects
                accessible_projects = await self._get_accessible_projects(user_id)
                query = query.where(Task.project_id.in_(accessible_projects))

            # Execute query
            result = await self.db.execute(query)
            tasks = result.scalars().all()

            # Organize by status
            kanban_board = TaskKanbanBoard(
                todo=[], in_progress=[], in_review=[], testing=[], done=[]
            )

            for task in tasks:
                task_response = TaskResponse.from_orm(task)
                task_status = getattr(task, "status", None)
                if task_status is None:
                    logger.warning(f"Task {task.id} has no status, skipping")
                    continue

                if task_status == "todo":
                    kanban_board.todo.append(task_response)
                elif task_status == "in_progress":
                    kanban_board.in_progress.append(task_response)
                elif task_status == "in_review":
                    kanban_board.in_review.append(task_response)
                elif task_status == "testing":
                    kanban_board.testing.append(task_response)
                elif task_status == "done":
                    kanban_board.done.append(task_response)

            return kanban_board

        except Exception as e:
            logger.error(f"Failed to get kanban board: {e}")
            raise

    async def _check_project_access(self, project_id: int, user_id: int) -> bool:
        """Check if user has access to project"""
        try:
            # Check if project is public
            project_result = await self.db.execute(
                select(Project).where(Project.id == project_id)
            )
            project = project_result.scalar_one_or_none()

            if not project:
                return False

            project_is_public = getattr(project, "is_public", False)

            if project_is_public:
                return True

            # Check if user is a member
            member_result = await self.db.execute(
                select(ProjectMember).where(
                    and_(
                        ProjectMember.project_id == project_id,
                        ProjectMember.user_id == user_id,
                    )
                )
            )

            return member_result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error(f"Failed to check project access: {e}")
            return False

    async def _check_task_access(self, task_id: int, user_id: int) -> bool:
        """Check if user has access to task"""
        try:
            task_result = await self.db.execute(select(Task).where(Task.id == task_id))
            task = task_result.scalar_one_or_none()

            if not task:
                return False

            # Task creator has access
            task_creator_id = getattr(task, "creator_id", None)
            if task_creator_id is None:
                logger.warning(f"Task {task_id} has no creator, access denied")
                return False

            if task_creator_id == user_id:
                return True

            # Check if user is assigned to task
            assignment_result = await self.db.execute(
                select(TaskAssignment).where(
                    and_(
                        TaskAssignment.task_id == task_id,
                        TaskAssignment.user_id == user_id,
                        TaskAssignment.is_active == True,
                    )
                )
            )
            if assignment_result.scalar_one_or_none():
                return True

            # Check project access
            task_project_id = getattr(task, "project_id", None)
            if task_project_id is None:
                logger.warning(f"Task {task_id} has no project, access denied")
                return False

            return await self._check_project_access(task_project_id, user_id)

        except Exception as e:
            logger.error(f"Failed to check task access: {e}")
            return False

    async def _get_accessible_projects(self, user_id: int) -> List[int]:
        """Get list of project IDs user has access to"""
        try:
            # Get public projects
            public_result = await self.db.execute(
                select(Project.id).where(Project.is_public == True)
            )
            public_projects = [row[0] for row in public_result.fetchall()]

            # Get projects where user is a member
            member_result = await self.db.execute(
                select(ProjectMember.project_id).where(ProjectMember.user_id == user_id)
            )
            member_projects = [row[0] for row in member_result.fetchall()]

            # Combine and deduplicate
            return list(set(public_projects + member_projects))

        except Exception as e:
            logger.error(f"Failed to get accessible projects: {e}")
            return []

    async def _assign_user_to_task(self, task_id: int, user_id: int, assigned_by: int):
        """Assign a user to a task"""
        try:
            # Verify user exists
            user_result = await self.db.execute(select(User).where(User.id == user_id))
            if not user_result.scalar_one_or_none():
                raise NotFoundError(f"User with ID {user_id} not found")

            # Check if already assigned
            existing_result = await self.db.execute(
                select(TaskAssignment).where(
                    and_(
                        TaskAssignment.task_id == task_id,
                        TaskAssignment.user_id == user_id,
                        TaskAssignment.is_active == True,
                    )
                )
            )
            if existing_result.scalar_one_or_none():
                return  # Already assigned

            # Create assignment
            assignment = TaskAssignment(
                task_id=task_id,
                user_id=user_id,
                assigned_by=assigned_by,
                is_active=True,
            )

            self.db.add(assignment)
            await self.db.flush()

        except Exception as e:
            logger.error(f"Failed to assign user {user_id} to task {task_id}: {e}")
            raise


async def get_task_service(db: AsyncSession | None = None) -> TaskService:
    """Get task service instance"""
    if db is None:
        async for session in get_async_session():
            return TaskService(session)
    return TaskService(cast(AsyncSession, db))
