"""
Dashboard Service

Business logic for dashboard analytics and summary.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, cast

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import TaskStatus
from core.database import get_async_session
from models.calendar import Event
from models.project import Project, ProjectMember
from models.task import Task, TaskAssignment
from models.user import UserActivityLog


class DashboardService:
    """Dashboard service for analytics and summary data"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_summary(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive dashboard summary for user"""
        project_stats = await self.get_project_stats(user_id)
        task_stats = await self.get_task_stats(user_id)
        recent_activity = await self.get_recent_activity(user_id)
        upcoming_events = await self.get_upcoming_events(user_id)

        return {
            "projects": project_stats,
            "tasks": task_stats,
            "recent_activity": recent_activity,
            "upcoming_events": upcoming_events,
            "last_updated": datetime.utcnow().isoformat(),
        }

    async def get_project_stats(self, user_id: int) -> Dict[str, Any]:
        """Get project statistics for user"""
        # Get projects user is member of
        member_query = select(ProjectMember.project_id).where(
            and_(ProjectMember.user_id == user_id, ProjectMember.is_active == True)
        )
        member_result = await self.db.execute(member_query)
        project_ids = [row[0] for row in member_result.fetchall()]

        if not project_ids:
            return {
                "total_projects": 0,
                "by_status": {},
                "by_priority": {},
                "owned_projects": 0,
            }

        # Total projects
        total_query = select(func.count(Project.id)).where(Project.id.in_(project_ids))
        total_result = await self.db.execute(total_query)
        total_projects = total_result.scalar()

        # Projects by status
        status_query = (
            select(Project.status, func.count(Project.id))
            .where(Project.id.in_(project_ids))
            .group_by(Project.status)
        )
        status_result = await self.db.execute(status_query)
        by_status = {status: count for status, count in status_result.fetchall()}

        # Projects by priority
        priority_query = (
            select(Project.priority, func.count(Project.id))
            .where(Project.id.in_(project_ids))
            .group_by(Project.priority)
        )
        priority_result = await self.db.execute(priority_query)
        by_priority = {
            priority: count for priority, count in priority_result.fetchall()
        }

        # Owned projects
        owned_query = select(func.count(Project.id)).where(
            Project.creator_id == user_id
        )
        owned_result = await self.db.execute(owned_query)
        owned_projects = owned_result.scalar()

        return {
            "total_projects": total_projects,
            "by_status": by_status,
            "by_priority": by_priority,
            "owned_projects": owned_projects,
        }

    async def get_task_stats(self, user_id: int) -> Dict[str, Any]:
        """Get task statistics for user"""
        # Get projects user has access to
        member_query = select(ProjectMember.project_id).where(
            and_(ProjectMember.user_id == user_id, ProjectMember.is_active == True)
        )
        member_result = await self.db.execute(member_query)
        project_ids = [row[0] for row in member_result.fetchall()]

        if not project_ids:
            return {
                "total_tasks": 0,
                "assigned_to_me": 0,
                "created_by_me": 0,
                "by_status": {},
                "by_priority": {},
                "overdue_tasks": 0,
            }

        # Total tasks in accessible projects
        total_query = select(func.count(Task.id)).where(
            Task.project_id.in_(project_ids)
        )
        total_result = await self.db.execute(total_query)
        total_tasks = total_result.scalar()

        # Tasks assigned to user
        assigned_query = (
            select(func.count(Task.id))
            .join(TaskAssignment)
            .where(
                and_(
                    Task.project_id.in_(project_ids),
                    TaskAssignment.user_id == user_id,
                    TaskAssignment.is_active == True,
                )
            )
        )
        assigned_result = await self.db.execute(assigned_query)
        assigned_to_me = assigned_result.scalar()

        # Tasks created by user
        created_query = select(func.count(Task.id)).where(
            and_(Task.project_id.in_(project_ids), Task.creator_id == user_id)
        )
        created_result = await self.db.execute(created_query)
        created_by_me = created_result.scalar()

        # Tasks by status (for assigned tasks)
        status_query = (
            select(Task.status, func.count(Task.id))
            .join(TaskAssignment)
            .where(
                and_(
                    Task.project_id.in_(project_ids),
                    TaskAssignment.user_id == user_id,
                    TaskAssignment.is_active == True,
                )
            )
            .group_by(Task.status)
        )
        status_result = await self.db.execute(status_query)
        by_status = {status: count for status, count in status_result.fetchall()}

        # Tasks by priority (for assigned tasks)
        priority_query = (
            select(Task.priority, func.count(Task.id))
            .join(TaskAssignment)
            .where(
                and_(
                    Task.project_id.in_(project_ids),
                    TaskAssignment.user_id == user_id,
                    TaskAssignment.is_active == True,
                )
            )
            .group_by(Task.priority)
        )
        priority_result = await self.db.execute(priority_query)
        by_priority = {
            priority: count for priority, count in priority_result.fetchall()
        }

        # Overdue tasks
        overdue_query = (
            select(func.count(Task.id))
            .join(TaskAssignment)
            .where(
                and_(
                    Task.project_id.in_(project_ids),
                    TaskAssignment.user_id == user_id,
                    TaskAssignment.is_active == True,
                    Task.due_date < datetime.utcnow(),
                    Task.status.in_(TaskStatus.get_incomplete_statuses()),
                )
            )
        )
        overdue_result = await self.db.execute(overdue_query)
        overdue_tasks = overdue_result.scalar()

        return {
            "total_tasks": total_tasks,
            "assigned_to_me": assigned_to_me,
            "created_by_me": created_by_me,
            "by_status": by_status,
            "by_priority": by_priority,
            "overdue_tasks": overdue_tasks,
        }

    async def get_recent_activity(
        self, user_id: int, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent activity for user"""
        query = (
            select(UserActivityLog)
            .where(UserActivityLog.user_id == user_id)
            .order_by(UserActivityLog.created_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        activities = result.scalars().all()

        return [
            {
                "id": activity.id,
                "action": activity.action,
                "resource_type": activity.resource_type,
                "resource_id": activity.resource_id,
                "description": activity.description,
                "created_at": activity.created_at.isoformat(),
            }
            for activity in activities
        ]

    async def get_upcoming_events(
        self, user_id: int, days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get upcoming events for user"""
        from models.calendar import Calendar

        end_date = datetime.utcnow() + timedelta(days=days)

        query = (
            select(Event)
            .join(Calendar)
            .where(
                and_(
                    Calendar.owner_id == user_id,
                    Event.start_datetime >= datetime.utcnow(),
                    Event.start_datetime <= end_date,
                )
            )
            .order_by(Event.start_datetime)
            .limit(10)
        )

        result = await self.db.execute(query)
        events = result.scalars().all()

        return [
            {
                "id": event.id,
                "title": event.title,
                "start_datetime": event.start_datetime.isoformat(),
                "end_datetime": event.end_datetime.isoformat(),
                "event_type": event.event_type.value,
                "location": event.location,
            }
            for event in events
        ]


async def get_dashboard_service(db: Optional[AsyncSession] = None) -> DashboardService:
    """Get dashboard service instance"""
    if db is None:
        async for session in get_async_session():
            return DashboardService(session)
    return DashboardService(cast(AsyncSession, db))
