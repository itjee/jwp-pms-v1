"""
Calendar Models

SQLAlchemy models for calendar and event management.
"""

import re
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.constants import (
    EventAttendeeStatus,
    EventReminder,
    EventStatus,
    EventType,
    RecurrenceType,
)
from core.database import Base

if TYPE_CHECKING:
    from models.project import Project
    from models.task import Task
    from models.user import User


class Calendar(Base):
    """
    Calendar model for organizing events
    """

    __tablename__ = "calendars"

    id = Column(Integer, primary_key=True, index=True, doc="Calendar ID")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), doc="Creation time"
    )
    created_by = Column(Integer, nullable=True, doc="User who created this calendar")
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), doc="Last update time"
    )
    updated_by = Column(
        Integer, nullable=True, doc="User who last updated this calendar"
    )

    # Basic Information
    name = Column(String(100), nullable=False, doc="Calendar name")
    description = Column(Text, nullable=True, doc="Calendar description")
    color = Column(
        String(7), default="#3B82F6", nullable=False, doc="Calendar color (hex)"
    )

    # Ownership and Visibility
    owner_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, doc="Calendar owner"
    )
    is_default = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is the user's default calendar",
    )
    is_public = Column(
        Boolean, default=False, nullable=False, doc="Whether the calendar is public"
    )
    is_active = Column(
        Boolean, default=True, nullable=False, doc="Whether the calendar is active"
    )

    # Relationships
    owner = relationship("User", back_populates="calendars")
    events = relationship(
        "Event", back_populates="calendar", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Calendar(id={self.id}, name='{self.name}', owner_id={self.owner_id})>"


class Event(Base):
    """
    Event model for calendar events
    """

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, doc="Event ID")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), doc="Creation time"
    )
    created_by = Column(Integer, nullable=True, doc="User who created this event")
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), doc="Last update time"
    )
    updated_by = Column(Integer, nullable=True, doc="User who last updated this event")

    # Basic Information
    title = Column(String(200), nullable=False, doc="Event title")
    description = Column(Text, nullable=True, doc="Event description")
    location = Column(String(200), nullable=True, doc="Event location")

    # Timing
    start_time = Column(
        DateTime(timezone=True), nullable=False, index=True, doc="Event start time"
    )
    end_time = Column(
        DateTime(timezone=True), nullable=False, index=True, doc="Event end time"
    )
    is_all_day = Column(
        Boolean, default=False, nullable=False, doc="Whether the event is all-day"
    )
    timezone = Column(String(50), nullable=True, doc="Event timezone")

    # Status and Type
    event_type = Column(
        String(20),  # Enum(EventType),
        default=EventType.MEETING,
        nullable=False,
        doc="Event type",
    )
    status = Column(
        String(20),  # Enum(EventStatus),
        default=EventStatus.SCHEDULED,
        nullable=False,
        doc="Event status",
    )

    # Associations
    calendar_id = Column(
        Integer, ForeignKey("calendars.id"), nullable=False, doc="Associated calendar"
    )
    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=True,
        doc="Associated project (optional)",
    )
    task_id = Column(
        Integer, ForeignKey("tasks.id"), nullable=True, doc="Associated task (optional)"
    )
    creator_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, doc="Event creator"
    )

    # Recurrence
    recurrence_type = Column(
        String(20),  # Enum(RecurrenceType),
        default=RecurrenceType.NONE,
        nullable=False,
        doc="Recurrence pattern",
    )
    recurrence_interval = Column(
        Integer,
        default=1,
        nullable=False,
        doc="Recurrence interval (e.g., every 2 weeks)",
    )
    recurrence_end_date = Column(
        DateTime(timezone=True), nullable=True, doc="When recurrence ends"
    )
    parent_event_id = Column(
        Integer,
        ForeignKey("events.id"),
        nullable=True,
        doc="Parent event for recurring instances",
    )

    # Notification
    reminder_type = Column(
        String(20),  # Enum(EventReminder),
        default=EventReminder.NONE,
        nullable=False,
        doc="Reminder type (e.g., email, push notification)",
    )

    reminder_minutes = Column(
        Integer, nullable=True, doc="Reminder time in minutes before event"
    )

    # Meeting Information
    meeting_url = Column(
        String(500), nullable=True, doc="Meeting URL (e.g., Zoom, Teams)"
    )
    meeting_id = Column(String(100), nullable=True, doc="Meeting ID")
    meeting_password = Column(String(100), nullable=True, doc="Meeting password")

    # Relationships
    calendar = relationship("Calendar", back_populates="events")
    project = relationship("Project", back_populates="events")
    task = relationship("Task", back_populates="events")
    creator = relationship(
        "User", back_populates="created_events", foreign_keys=[creator_id]
    )

    # parent_event = relationship("Event", remote_side=[Base.id])
    parent_event = relationship(
        "Event", remote_side=lambda: Event.id, back_populates="recurring_instances"
    )

    recurring_instances = relationship(
        "Event", back_populates="parent_event", cascade="all, delete-orphan"
    )

    attendees = relationship(
        "EventAttendee", back_populates="event", cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("start_time <= end_time", name="ck_event_time_order"),
        CheckConstraint(
            "recurrence_interval > 0", name="ck_event_recurrence_interval_positive"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Event(id={self.id}, title='{self.title}', start_time={self.start_time})>"
        )


class EventAttendee(Base):
    """
    Event attendee model
    """

    __tablename__ = "event_attendees"

    id = Column(Integer, primary_key=True, index=True, doc="Attendee ID")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), doc="Creation time"
    )
    created_by = Column(
        Integer, nullable=True, doc="User who created this attendee record"
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), doc="Last update time"
    )
    updated_by = Column(
        Integer, nullable=True, doc="User who last updated this attendee record"
    )

    # Basic Information

    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, doc="Event ID")
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, doc="Attendee user ID"
    )
    status = Column(
        String(20),
        default=EventAttendeeStatus.INVITED,
        nullable=False,
        doc="Attendance status (invited, accepted, declined, tentative)",
    )
    response_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the user responded to the invitation",
    )
    is_organizer = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the attendee is the organizer",
    )

    # Relationships
    event = relationship("Event", back_populates="attendees")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<EventAttendee(event_id={self.event_id}, user_id={self.user_id}, status='{self.status}')>"
