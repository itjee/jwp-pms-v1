"""
System Information API Routes

System and application information endpoints.
"""

import platform
import sys
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from core.config import settings

router = APIRouter()


@router.get("/info")
async def system_info():
    """
    Get system and application information
    """
    return JSONResponse(
        {
            "application": {
                "name": settings.PROJECT_NAME,
                "version": settings.VERSION,
                "environment": settings.ENVIRONMENT,
                "debug": settings.DEBUG,
                "api_version": "v1",
            },
            "system": {
                "platform": platform.platform(),
                "python_version": sys.version,
                "architecture": platform.architecture()[0],
                "hostname": platform.node(),
            },
            "configuration": {
                "database_configured": bool(settings.DATABASE_URL),
                "cors_enabled": bool(settings.BACKEND_CORS_ORIGINS),
                "upload_path": settings.UPLOAD_PATH,
                "max_file_size": f"{settings.MAX_FILE_SIZE / 1024 / 1024:.1f} MB",
            },
            "features": {
                "user_management": True,
                "project_management": True,
                "task_management": True,
                "calendar_management": True,
                "file_upload": True,
                "oauth_support": bool(
                    settings.GOOGLE_CLIENT_ID or settings.GITHUB_CLIENT_ID
                ),
                "email_support": bool(settings.SMTP_HOST),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@router.get("/version")
async def version_info():
    """
    Get application version information
    """
    return JSONResponse(
        {
            "version": settings.VERSION,
            "api_version": "v1",
            "build_date": "2024-01-01",  # Can be set during build
            "commit_hash": "development",  # Can be set during build
            "environment": settings.ENVIRONMENT,
        }
    )


@router.get("/status")
async def application_status():
    """
    Get current application status
    """
    # Check if critical directories exist
    uploads_dir = Path(settings.UPLOAD_PATH)

    status = {
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "healthy",
            "database": "checking...",  # Will be updated by health check
            "file_system": "healthy" if uploads_dir.exists() else "degraded",
        },
        "metrics": {
            "uptime": "Just started",  # Can be enhanced
            "total_requests": "N/A",  # Can be enhanced with middleware
            "active_connections": "N/A",  # Can be enhanced
        },
    }

    return JSONResponse(status)


@router.get("/endpoints")
async def list_endpoints():
    """
    List available API endpoints
    """
    endpoints = {
        "documentation": {
            "swagger_ui": "/docs" if settings.DEBUG else "Disabled",
            "redoc": "/redoc" if settings.DEBUG else "Disabled",
            "openapi_spec": (
                f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else "Disabled"
            ),
        },
        "health": {
            "basic": "/health",
            "detailed": f"{settings.API_V1_STR}/health/detailed",
            "readiness": f"{settings.API_V1_STR}/health/ready",
            "liveness": f"{settings.API_V1_STR}/health/live",
        },
        "system": {
            "info": f"{settings.API_V1_STR}/info",
            "version": f"{settings.API_V1_STR}/version",
            "status": f"{settings.API_V1_STR}/status",
            "endpoints": f"{settings.API_V1_STR}/endpoints",
        },
        "api": {"root": "/", "api_root": settings.API_V1_STR, "uploads": "/uploads"},
        "future_endpoints": {
            "authentication": f"{settings.API_V1_STR}/auth/*",
            "users": f"{settings.API_V1_STR}/users/*",
            "projects": f"{settings.API_V1_STR}/projects/*",
            "tasks": f"{settings.API_V1_STR}/tasks/*",
            "calendar": f"{settings.API_V1_STR}/calendar/*",
            "graphql": "/graphql",
        },
    }

    return JSONResponse(endpoints)
