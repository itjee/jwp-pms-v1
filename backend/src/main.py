"""
PMS Backend API Main Application

FastAPI application with GraphQL support for Project Management System.
"""

import logging
import socket
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from core.config import settings
from core.database import check_database_connection, create_tables
from utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan events
    """
    # Startup
    logger.info("🚀 Starting PMS Backend API...")
    logger.info(f"🌍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔧 Debug mode: {settings.DEBUG}")

    # Check database connection
    try:
        db_connected = await check_database_connection()
        if db_connected:
            logger.info("✅ Database connection verified")

            # Create database tables if they don't exist (only in development)
            if settings.ENVIRONMENT == "development":
                await create_tables()
                logger.info("✅ Database tables created/verified")
        else:
            logger.warning("⚠️ Database connection failed - some features may not work")
    except Exception as e:
        logger.error(f"❌ Database setup error: {e}")

    logger.info(f"📊 API Documentation: /docs")
    logger.info(f"🔧 Health check: /health")
    logger.info("✨ PMS Backend API is ready!")

    yield

    # Shutdown
    logger.info("🛑 Shutting down PMS Backend API...")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    Project Management System Backend API
    
    A comprehensive project management system with user management, 
    project tracking, task management, and calendar functionality.
    
    ## Features
    * 👥 User Management & Authentication
    * 📁 Project Management
    * ✅ Task Tracking
    * 📅 Calendar & Events
    * 🔐 Role-based Access Control
    """,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
    contact={
        "name": "PMS Team",
        "email": "team@pms.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "*.localhost", "*"]
)

# Add CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    logger.info(f"🌐 CORS enabled for origins: {settings.BACKEND_CORS_ORIGINS}")

# Static files
uploads_dir = Path(settings.UPLOAD_PATH)
uploads_dir.mkdir(exist_ok=True)

app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return JSONResponse(
        {
            "message": f"🚀 {settings.PROJECT_NAME} is running!",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "status": "healthy",
            "endpoints": {
                "health": "/health",
                "docs": "/docs" if settings.DEBUG else "Disabled in production",
                "redoc": "/redoc" if settings.DEBUG else "Disabled in production",
                "api": settings.API_V1_STR,
            },
            "features": {
                "user_management": "✅ Available",
                "project_management": "✅ Available",
                "task_management": "✅ Available",
                "calendar": "✅ Available",
                "file_upload": "✅ Available",
            },
        }
    )


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    try:
        # Check database connection
        db_status = await check_database_connection()

        return JSONResponse(
            {
                "status": "healthy" if db_status else "degraded",
                "version": settings.VERSION,
                "environment": settings.ENVIRONMENT,
                "timestamp": "2024-01-01T00:00:00Z",  # Will be replaced with actual timestamp
                "checks": {
                    "database": "✅ Connected" if db_status else "❌ Disconnected",
                    "api": "✅ Running",
                    "uploads": "✅ Available",
                },
                "uptime": "Just started",  # Can be enhanced with actual uptime
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2024-01-01T00:00:00Z",
            },
        )


@app.get(f"{settings.API_V1_STR}/info")
async def api_info():
    """
    API information endpoint
    """
    return JSONResponse(
        {
            "api_version": "v1",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "features": {
                "authentication": "JWT + OAuth2",
                "database": "PostgreSQL with SQLAlchemy",
                "api_style": "REST + GraphQL (coming soon)",
                "file_storage": "Local filesystem",
                "real_time": "WebSocket (planned)",
            },
            "endpoints": {
                "health": "/health",
                "root": "/",
                "docs": "/docs",
                "uploads": "/uploads",
            },
        }
    )


from api.auth import router as auth_router
from api.calendar import router as calendar_router
from api.dashboard import router as dashboard_router

# Include API routes
from api.health import router as health_router
from api.projects import router as projects_router
from api.system import router as system_router
from api.tasks import router as tasks_router
from api.uploads import router as uploads_router
from api.users import router as users_router

app.include_router(health_router, prefix=settings.API_V1_STR, tags=["health"])
app.include_router(system_router, prefix=settings.API_V1_STR, tags=["system"])
app.include_router(
    auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"]
)
app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(
    projects_router, prefix=f"{settings.API_V1_STR}/projects", tags=["projects"]
)
app.include_router(tasks_router, prefix=f"{settings.API_V1_STR}/tasks", tags=["tasks"])
app.include_router(
    calendar_router, prefix=f"{settings.API_V1_STR}/calendar", tags=["calendar"]
)
app.include_router(
    dashboard_router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["dashboard"]
)
app.include_router(
    uploads_router, prefix=f"{settings.API_V1_STR}/uploads", tags=["uploads"]
)

# TODO: Add these when implemented
# from src.api.auth import router as auth_router
# from src.api.users import router as users_router
# from src.api.projects import router as projects_router
# from src.api.tasks import router as tasks_router

# app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
# app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
# app.include_router(projects_router, prefix=f"{settings.API_V1_STR}/projects", tags=["projects"])
# app.include_router(tasks_router, prefix=f"{settings.API_V1_STR}/tasks", tags=["tasks"])

# TODO: Add GraphQL endpoint
# from src.api.graphql import graphql_app
# app.mount("/graphql", graphql_app)


def find_free_port(start_port: int = 8000) -> int:
    """
    Find a free port starting from start_port
    """
    for port in range(start_port, start_port + 10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    return 8080  # fallback


def main():
    """
    Main function to run the application
    """
    # Find available port
    port = find_free_port(8000)
    host = "127.0.0.1"

    logger.info(f"🚀 Starting {settings.PROJECT_NAME}")
    logger.info(f"🌐 Server URL: http://{host}:{port}")
    logger.info(f"📖 API Docs: http://{host}:{port}/docs")
    logger.info(f"🔧 Health Check: http://{host}:{port}/health")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
        access_log=settings.DEBUG,
        reload_dirs=["src"] if settings.DEBUG else None,
    )


if __name__ == "__main__":
    main()
