"""
Database Utilities

Helper functions for database operations and health checks.
"""

import logging
from typing import Any, Dict, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal, engine

logger = logging.getLogger(__name__)


async def check_database_health() -> Dict[str, Any]:
    """
    Comprehensive database health check
    """
    health_info = {
        "status": "unknown",
        "connection": False,
        "tables": [],
        "version": None,
        "error": None,
    }

    try:
        async with engine.begin() as conn:
            # Basic connection test
            result = await conn.execute(text("SELECT 1"))
            health_info["connection"] = result.fetchone() is not None

            # Get database version
            try:
                version_result = await conn.execute(text("SELECT version()"))
                version_row = version_result.fetchone()
                if version_row:
                    health_info["version"] = version_row[0]
            except Exception as e:
                logger.warning(f"Could not get database version: {e}")

            # Check if our tables exist
            try:
                tables_result = await conn.execute(
                    text(
                        """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """
                    )
                )
                health_info["tables"] = [row[0] for row in tables_result.fetchall()]
            except Exception as e:
                logger.warning(f"Could not list tables: {e}")

            health_info["status"] = "healthy"

    except Exception as e:
        health_info["status"] = "unhealthy"
        health_info["error"] = str(e)
        logger.error(f"Database health check failed: {e}")

    return health_info


async def test_database_operations() -> Dict[str, Any]:
    """
    Test basic database operations
    """
    test_results = {
        "connection": False,
        "create_session": False,
        "query_execution": False,
        "transaction": False,
        "error": None,
    }

    try:
        # Test connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            test_results["connection"] = True

        # Test session creation
        async with AsyncSessionLocal() as session:
            test_results["create_session"] = True

            # Test query execution
            result = await session.execute(text("SELECT CURRENT_TIMESTAMP"))
            timestamp = result.fetchone()
            if timestamp:
                test_results["query_execution"] = True

            # Test transaction
            try:
                await session.execute(text("SELECT 1"))
                await session.commit()
                test_results["transaction"] = True
            except Exception as e:
                await session.rollback()
                raise e

    except Exception as e:
        test_results["error"] = str(e)
        logger.error(f"Database operations test failed: {e}")

    return test_results


async def get_database_stats() -> Dict[str, Any]:
    """
    Get database statistics and information
    """
    stats = {
        "database_size": None,
        "table_count": 0,
        "connection_count": None,
        "uptime": None,
        "error": None,
    }

    try:
        async with engine.begin() as conn:
            # Get database size
            try:
                size_result = await conn.execute(
                    text(
                        """
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                """
                    )
                )
                size_row = size_result.fetchone()
                if size_row:
                    stats["database_size"] = size_row[0]
            except Exception as e:
                logger.warning(f"Could not get database size: {e}")

            # Get table count
            try:
                count_result = await conn.execute(
                    text(
                        """
                    SELECT COUNT(*)
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """
                    )
                )
                count_row = count_result.fetchone()
                if count_row:
                    stats["table_count"] = count_row[0]
            except Exception as e:
                logger.warning(f"Could not get table count: {e}")

            # Get connection count
            try:
                conn_result = await conn.execute(
                    text(
                        """
                    SELECT COUNT(*) 
                    FROM pg_stat_activity 
                    WHERE state = 'active'
                """
                    )
                )
                conn_row = conn_result.fetchone()
                if conn_row:
                    stats["connection_count"] = conn_row[0]
            except Exception as e:
                logger.warning(f"Could not get connection count: {e}")

            # Get uptime
            try:
                uptime_result = await conn.execute(
                    text(
                        """
                    SELECT date_trunc('second', current_timestamp - pg_postmaster_start_time())
                """
                    )
                )
                uptime_row = uptime_result.fetchone()
                if uptime_row:
                    stats["uptime"] = str(uptime_row[0])
            except Exception as e:
                logger.warning(f"Could not get uptime: {e}")

    except Exception as e:
        stats["error"] = str(e)
        logger.error(f"Failed to get database stats: {e}")

    return stats


async def initialize_database():
    """
    Initialize database with basic setup
    """
    logger.info("🔧 Initializing database...")

    try:
        # Check connection
        health = await check_database_health()
        if health["status"] != "healthy":
            raise Exception(
                f"Database unhealthy: {health.get('error', 'Unknown error')}"
            )

        # Import all models to ensure they're registered
        from models import (
            Calendar,
            Event,
            Project,
            ProjectMember,
            Tag,
            Task,
            TaskAssignment,
            User,
        )

        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(
                lambda sync_conn: logger.info("📊 Creating database tables...")
            )
            await conn.run_sync(
                lambda sync_conn: __import__(
                    "core.database", fromlist=["Base"]
                ).Base.metadata.create_all(sync_conn)
            )

        logger.info("✅ Database initialization completed")
        return True

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False


async def reset_database():
    """
    Reset database (drop and recreate all tables) - Use with caution!
    """
    logger.warning("⚠️ Resetting database - all data will be lost!")

    try:
        from core.database import Base

        async with engine.begin() as conn:
            # Drop all tables
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("🗑️ All tables dropped")

            # Recreate all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("📊 All tables recreated")

        logger.info("✅ Database reset completed")
        return True

    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        return False
