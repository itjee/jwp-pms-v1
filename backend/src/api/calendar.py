"""
Calendar API Routes

Calendar and event management endpoints.
"""

import logging
from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from core.dependencies import get_current_active_user
from models.user import User
from schemas.calendar import CalendarResponse, EventCreate, EventResponse, EventUpdate
from services.calendar import CalendarService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/events", response_model=List[EventResponse])
async def list_events(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    calendar_id: Optional[int] = Query(None, description="Filter by calendar"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    List events for current user
    """
    try:
        calendar_service = CalendarService(db)
        events = await calendar_service.list_user_events(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            calendar_id=calendar_id,
        )

        return [EventResponse.from_orm(event) for event in events]

    except Exception as e:
        logger.error(f"Error listing events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve events",
        )


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get event by ID
    """
    try:
        calendar_service = CalendarService(db)
        event = await calendar_service.get_event_with_access_check(
            event_id, current_user.id
        )

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
            )

        return EventResponse.from_orm(event)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event {event_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve event",
        )


@router.post(
    "/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED
)
async def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Create a new event
    """
    try:
        calendar_service = CalendarService(db)
        event = await calendar_service.create_event(event_data, current_user.id)

        logger.info(f"Event created by {current_user.name}: {event.title}")

        return EventResponse.from_orm(event)

    except Exception as e:
        logger.error(f"Error creating event: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create event",
        )


@router.put("/events/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Update event
    """
    try:
        calendar_service = CalendarService(db)
        event = await calendar_service.update_event(
            event_id, event_data, current_user.id
        )

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
            )

        logger.info(f"Event updated by {current_user.name}: {event.title}")

        return EventResponse.from_orm(event)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating event {event_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update event",
        )


@router.delete("/events/{event_id}")
async def delete_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Delete event
    """
    try:
        calendar_service = CalendarService(db)
        success = await calendar_service.delete_event(event_id, current_user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
            )

        logger.info(f"Event deleted by {current_user.name}: {event_id}")

        return {"message": "Event deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete event",
        )


@router.get("/calendars", response_model=List[CalendarResponse])
async def list_calendars(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    List calendars for current user
    """
    try:
        calendar_service = CalendarService(db)
        calendars = await calendar_service.list_user_calendars(current_user.id)

        return [CalendarResponse.from_orm(calendar) for calendar in calendars]

    except Exception as e:
        logger.error(f"Error listing calendars: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve calendars",
        )
