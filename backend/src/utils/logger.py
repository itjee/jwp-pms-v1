"""
Logging Configuration

Structured logging setup for the PMS application.
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Any, Dict

from core.config import settings


def setup_logging():
    """
    Setup logging configuration
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Logging configuration
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d, "message": "%(message)s"}',
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "default",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": log_dir / "pms_backend.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": log_dir / "pms_backend_errors.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
        },
        "loggers": {
            "src": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console", "error_file"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "alembic": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
    }

    # Apply configuration
    logging.config.dictConfig(config)

    # Log setup completion
    logger = logging.getLogger(__name__)
    logger.info(f"🔧 Logging setup complete - Level: {settings.LOG_LEVEL}")


class StructuredLogger:
    """
    Structured logger for consistent logging format
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def info(self, message: str, **kwargs):
        """Log info message with structured data"""
        extra_data = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {extra_data}" if extra_data else message
        self.logger.info(full_message)

    def error(self, message: str, error: Exception = None, **kwargs):  # type: ignore
        """Log error message with structured data"""
        extra_data = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        if error:
            extra_data = (
                f"error={str(error)} | {extra_data}"
                if extra_data
                else f"error={str(error)}"
            )
        full_message = f"{message} | {extra_data}" if extra_data else message
        self.logger.error(full_message)

    def warning(self, message: str, **kwargs):
        """Log warning message with structured data"""
        extra_data = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {extra_data}" if extra_data else message
        self.logger.warning(full_message)

    def debug(self, message: str, **kwargs):
        """Log debug message with structured data"""
        extra_data = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {extra_data}" if extra_data else message
        self.logger.debug(full_message)


def get_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger instance
    """
    return StructuredLogger(name)
