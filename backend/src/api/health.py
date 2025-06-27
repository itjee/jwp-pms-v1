"""
Health Check API Routes

System health monitoring endpoints.
"""

from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_async_session
from core.db_utils import (
    check_database_health,
    get_database_stats,
    test_database_operations,
)

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint
    """
    return JSONResponse(
        {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
        }
    )


@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with database and service status
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {},
    }

    # Database health check
    try:
        db_health = await check_database_health()
        health_status["checks"]["database"] = {
            "status": "healthy" if db_health["status"] == "healthy" else "unhealthy",
            "connection": db_health["connection"],
            "tables_count": len(db_health["tables"]),
            "version": db_health["version"],
            "error": db_health.get("error"),
        }

        if db_health["status"] != "healthy":
            health_status["status"] = "degraded"

    except Exception as e:
        health_status["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"

    # API check
    health_status["checks"]["api"] = {
        "status": "healthy",
        "message": "API is responding",
    }

    # File system check
    try:
        from pathlib import Path

        uploads_path = Path(settings.UPLOAD_PATH)
        uploads_path.mkdir(exist_ok=True)
        health_status["checks"]["filesystem"] = {
            "status": "healthy",
            "upload_directory": str(uploads_path),
            "writable": uploads_path.exists() and uploads_path.is_dir(),
        }
    except Exception as e:
        health_status["checks"]["filesystem"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"

    # Set final status
    if health_status["status"] == "degraded":
        return JSONResponse(status_code=503, content=health_status)

    return JSONResponse(health_status)


@router.get("/health/database")
async def database_health_check():
    """
    Comprehensive database health check
    """
    try:
        # Get database health
        db_health = await check_database_health()

        # Test database operations
        db_operations = await test_database_operations()

        # Get database statistics
        db_stats = await get_database_stats()

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "health": db_health,
            "operations": db_operations,
            "statistics": db_stats,
            "overall_status": (
                "healthy"
                if (
                    db_health["status"] == "healthy"
                    and db_operations["connection"]
                    and db_operations["create_session"]
                )
                else "unhealthy"
            ),
        }

        if result["overall_status"] == "unhealthy":
            return JSONResponse(status_code=503, content=result)

        return JSONResponse(result)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error",
                "error": str(e),
            },
        )


@router.get("/health/ready")
async def readiness_check():
    """
    Kubernetes readiness probe endpoint
    """
    try:
        # Quick database check
        db_health = await check_database_health()

        if db_health["status"] == "healthy" and db_health["connection"]:
            return JSONResponse(
                {
                    "status": "ready",
                    "timestamp": datetime.utcnow().isoformat(),
                    "database": "connected",
                    "tables": len(db_health["tables"]),
                }
            )
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not ready",
                    "reason": "Database not accessible",
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": db_health.get("error"),
                },
            )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not ready",
                "reason": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


@router.get("/health/live")
async def liveness_check():
    """
    Kubernetes liveness probe endpoint
    """
    return JSONResponse(
        {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
        }
    )


@router.get("/health/info")
async def health_info():
    """
    Health check information endpoint
    """
    return JSONResponse(
        {
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "documentation": {
                "swagger_ui": "/docs" if settings.DEBUG else "Disabled",
                "redoc": "/redoc" if settings.DEBUG else "Disabled",
                "openapi_spec": (
                    f"{settings.API_V1_STR}/openapi.json"
                    if settings.DEBUG
                    else "Disabled"
                ),
            },
        }
    )


@router.get("/health/endpoints")
async def health_endpoints():
    """
    List available health check endpoints
    """
    return JSONResponse(
        {
            "endpoints": {
                "basic": "/health",
                "detailed": "/health/detailed",
                "database": "/health/database",
                "readiness": "/health/ready",
                "liveness": "/health/live",
                "info": "/health/info",
            },
            "documentation": {
                "swagger_ui": "/docs" if settings.DEBUG else "Disabled",
                "redoc": "/redoc" if settings.DEBUG else "Disabled",
            },
        }
    )


@router.get("/health/system")
async def system_health_check():
    """
    System health check endpoint
    """
    try:
        # Perform basic health checks
        db_health = await check_database_health()
        if db_health["status"] != "healthy":
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "reason": "Database connection failed",
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": db_health.get("error"),
                },
            )

        return JSONResponse(
            {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": settings.PROJECT_NAME,
                "version": settings.VERSION,
                "environment": settings.ENVIRONMENT,
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


@router.get("/health/system/info")
async def system_health_info():
    """
    System health information endpoint
    """
    return JSONResponse(
        {
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "documentation": {
                "swagger_ui": "/docs" if settings.DEBUG else "Disabled",
                "redoc": "/redoc" if settings.DEBUG else "Disabled",
                "openapi_spec": (
                    f"{settings.API_V1_STR}/openapi.json"
                    if settings.DEBUG
                    else "Disabled"
                ),
            },
        }
    )


@router.get("/health/system/endpoints")
async def system_health_endpoints():
    """
    List available system health check endpoints
    """
    return JSONResponse(
        {
            "endpoints": {
                "basic": "/health/system",
                "info": "/health/system/info",
            },
            "documentation": {
                "swagger_ui": "/docs" if settings.DEBUG else "Disabled",
                "redoc": "/redoc" if settings.DEBUG else "Disabled",
            },
        }
    )


@router.get("/health/system/ready")
async def system_readiness_check():
    """
    System readiness check endpoint
    """
    try:
        # Perform database readiness check
        db_health = await check_database_health()
        if db_health["status"] != "healthy":
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not ready",
                    "reason": "Database not accessible",
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": db_health.get("error"),
                },
            )

        return JSONResponse(
            {
                "status": "ready",
                "timestamp": datetime.utcnow().isoformat(),
                "service": settings.PROJECT_NAME,
                "version": settings.VERSION,
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not ready",
                "reason": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


@router.get("/health/system/live")
async def system_liveness_check():
    """
    System liveness check endpoint
    """
    return JSONResponse(
        {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
        }
    )
