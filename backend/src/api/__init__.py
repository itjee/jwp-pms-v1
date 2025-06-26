"""
API Routes Package

FastAPI routes and GraphQL endpoints.
"""

from .auth import router as auth_router
from .calendar import router as calendar_router
from .health import router as health_router
from .projects import router as projects_router
from .system import router as system_router
from .tasks import router as tasks_router
from .users import router as users_router

__all__ = [
    "auth_router",
    "users_router",
    "projects_router",
    "tasks_router",
    "calendar_router",
    "health_router",
    "system_router",
]
