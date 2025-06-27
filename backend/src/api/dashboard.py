"""
Dashboard API Routes

Dashboard analytics and summary endpoints.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from core.dependencies import get_current_active_user
from models.user import User
from services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    """
    Get dashboard summary for current user
    """
    try:
        dashboard_service = DashboardService(db)
        summary = await dashboard_service.get_user_summary(current_user.id)

        return summary

    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard summary",
        )


@router.get("/projects/stats")
async def get_project_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    """
    Get project statistics for current user
    """
    try:
        dashboard_service = DashboardService(db)
        stats = await dashboard_service.get_project_stats(current_user.id)

        return stats

    except Exception as e:
        logger.error(f"Error getting project stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve project statistics",
        )


@router.get("/tasks/stats")
async def get_task_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    """
    Get task statistics for current user
    """
    try:
        dashboard_service = DashboardService(db)
        stats = await dashboard_service.get_task_stats(current_user.id)

        return stats

    except Exception as e:
        logger.error(f"Error getting task stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task statistics",
        )


@router.get("/activity")
async def get_recent_activity(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
) -> Dict[str, Any]:
    """
    Get recent activity for current user
    """
    try:
        dashboard_service = DashboardService(db)
        activity = await dashboard_service.get_recent_activity(current_user.id)

        return activity

    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent activity",
        )
