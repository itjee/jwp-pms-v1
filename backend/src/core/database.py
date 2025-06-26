"""
Database Configuration

SQLAlchemy async database setup for PostgreSQL.
"""

import logging
from typing import AsyncGenerator

from core.config import get_database_url
from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = get_database_url()

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    future=True,
    poolclass=NullPool,  # Disable connection pooling for development
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create declarative base
Base = declarative_base()

# Naming convention for constraints
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

Base.metadata = MetaData(naming_convention=naming_convention)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """
    Create all database tables
    """
    try:
        async with engine.begin() as conn:
            # Import all models to register them with Base
            from models import (  # noqa
                Calendar,
                Event,
                Project,
                Task,
                User,
                calendar,
                project,
                task,
                user,
            )

            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        raise


async def drop_tables():
    """
    Drop all database tables (use with caution!)
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.warning("⚠️ All database tables dropped")
    except Exception as e:
        logger.error(f"❌ Error dropping database tables: {e}")
        raise


async def check_database_connection():
    """
    Check if database connection is working
    """
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


# For Alembic migrations
def get_sync_engine():
    """
    Get synchronous engine for Alembic migrations
    """
    from core.config import get_sync_database_url
    from sqlalchemy import create_engine

    return create_engine(get_sync_database_url())
