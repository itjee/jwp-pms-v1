"""
Logging Configuration

Centralized logging setup for the PMS application.
"""

import functools
import logging
import logging.config
import logging.handlers
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from core.config import settings


# Setup logging configuration
# 전체 로깅 설정
# 콘솔, 파일, 에러 파일 핸들러를 포함
# 로테이팅 파일 핸들러(10BMB, 5개 백업) 사용
# JSON, 기본, 상세 포맷터를 사용
def setup_logging():
    """Setup application logging configuration"""

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Logging configuration
    logging_config: Dict[str, Any] = {
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
                "format": "%(asctime)s %(name)s %(levelname)s %(module)s %(funcName)s %(lineno)d %(message)s",
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
                "filename": "logs/pms.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": "logs/pms_errors.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
        },
        "loggers": {
            # Root logger
            "": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            # Application loggers
            "pms": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "core": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "services": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "api": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "utils": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            # Third-party loggers
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "sqlalchemy.dialects": {
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
    }

    # Apply configuration
    logging.config.dictConfig(logging_config)

    # Set up security and audit loggers
    setup_security_logging()
    setup_audit_logging()


# 보안 이벤트 로깅
def setup_security_logging():
    """Setup security-specific logging"""

    # Create security logger
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplication
    security_logger.handlers.clear()

    # Security log handler
    security_handler = logging.handlers.RotatingFileHandler(
        "logs/security.log", maxBytes=10485760, backupCount=10, encoding="utf8"  # 10MB
    )

    # Security log formatter
    security_formatter = logging.Formatter(
        "%(asctime)s - SECURITY - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    security_handler.setFormatter(security_formatter)
    security_logger.addHandler(security_handler)
    security_logger.propagate = False

    return security_logger


# 감사 로그 (컴플라이언스용)
def setup_audit_logging():
    """Setup audit logging for compliance"""

    # Create audit logger
    audit_logger = logging.getLogger("audit")
    audit_logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplication
    audit_logger.handlers.clear()

    # Audit log handler
    audit_handler = logging.handlers.RotatingFileHandler(
        "logs/audit.log",
        maxBytes=10485760,  # 10MB
        backupCount=20,  # Keep more audit logs
        encoding="utf8",
    )

    # Audit log formatter (structured for easy parsing)
    audit_formatter = logging.Formatter(
        "%(asctime)s|%(levelname)s|%(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    audit_handler.setFormatter(audit_formatter)
    audit_logger.addHandler(audit_handler)
    audit_logger.propagate = False

    return audit_logger


# 클래스에 로깅 기능을 추가하는 믹스인 클래스
class LoggerMixin:
    """Mixin class to add logging capabilities"""

    @property
    def logger(self) -> logging.Logger:
        """Get logger instance for the class"""
        return logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )


# 로거 인스턴스 생성 함수
def get_logger(name: str | None = None) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name or __name__)


# 컨텍스트 매니저로 로그에 추가 정보 포함
class LogContext:
    """Context manager for adding context to log messages"""

    def __init__(self, **context):
        self.context = context
        self.old_factory = logging.getLogRecordFactory()

    def __enter__(self):
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.old_factory)


# 함수 호출 로깅
def log_function_call(func):
    """Decorator to log function calls"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)

        # Log function entry
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {e}")
            raise

    return wrapper


# 비동기 함수 호출 로깅
def log_async_function_call(func):
    """Decorator to log async function calls"""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)

        # Log function entry
        logger.debug(f"Calling async {func.__name__} with args={args}, kwargs={kwargs}")

        try:
            result = await func(*args, **kwargs)
            logger.debug(f"Async {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Async {func.__name__} failed with error: {e}")
            raise

    return wrapper


# 구조화된 로깅
class StructuredLogger:
    """Structured logging helper"""

    def __init__(self, name: str | None = None):
        self.logger = get_logger(name)

    def info(self, message: str, **context):
        """Log info message with structured context"""
        extra = {"context": context} if context else {}
        self.logger.info(message, extra=extra)

    def error(self, message: str, **context):
        """Log error message with structured context"""
        extra = {"context": context} if context else {}
        self.logger.error(message, extra=extra)

    def warning(self, message: str, **context):
        """Log warning message with structured context"""
        extra = {"context": context} if context else {}
        self.logger.warning(message, extra=extra)

    def debug(self, message: str, **context):
        """Log debug message with structured context"""
        extra = {"context": context} if context else {}
        self.logger.debug(message, extra=extra)

    def exception(self, message: str, **context):
        """Log exception with structured context"""
        extra = {"context": context} if context else {}
        self.logger.exception(message, extra=extra)


# 보안 이벤트 로깅
def log_security_event(
    event_type: str, user_id: int | None = None, details: str = "", **context
):
    """Log security event"""
    security_logger = logging.getLogger("security")

    message = f"EVENT:{event_type}"
    if user_id:
        message += f"|USER:{user_id}"
    if details:
        message += f"|DETAILS:{details}"

    for key, value in context.items():
        message += f"|{key.upper()}:{value}"

    security_logger.info(message)


# 감사 이벤트 로깅
def log_audit_event(
    action: str,
    user_id: int,
    resource_type: str | None = None,
    resource_id: int | None = None,
    details: str = "",
    **context,
):
    """Log audit event"""
    audit_logger = logging.getLogger("audit")

    message = f"ACTION:{action}|USER:{user_id}"

    if resource_type:
        message += f"|RESOURCE_TYPE:{resource_type}"
    if resource_id:
        message += f"|RESOURCE_ID:{resource_id}"
    if details:
        message += f"|DETAILS:{details}"

    for key, value in context.items():
        message += f"|{key.upper()}:{value}"

    audit_logger.info(message)


def setup_request_id_context():
    """Setup request ID context for tracing requests"""
    try:
        import contextvars

        # Create context variable for request ID
        request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
            "request_id", default=""
        )

        # Custom formatter that includes request ID
        class RequestIdFormatter(logging.Formatter):
            def format(self, record):
                request_id = request_id_var.get("")
                if request_id:
                    record.request_id = request_id
                    if hasattr(record, "getMessage"):
                        original_format = self._style._fmt
                        self._style._fmt = f"[{request_id}] {original_format}"

                result = super().format(record)

                # Reset format
                if request_id and hasattr(record, "getMessage"):
                    self._style._fmt = original_format

                return result

        # Store context variable for use in middleware
        setattr(logging, "request_id_var", request_id_var)
        # logging.request_id_var = request_id_var

    except ImportError:
        # contextvars not available in older Python versions
        pass


# Initialize request ID context
setup_request_id_context()


# 작업 시간 측정 및 로깅
class TimedLogger:
    """Logger that tracks timing information"""

    def __init__(self, logger_name: str | None = None):
        self.logger = get_logger(logger_name)
        self.start_time = None

    def start_timer(self, operation: str):
        """Start timing an operation"""
        import time

        self.start_time = time.time()
        self.operation = operation
        self.logger.debug(f"Starting operation: {operation}")

    def end_timer(self, success: bool = True):
        """End timing and log result"""
        if self.start_time is None:
            self.logger.warning("Timer was not started")
            return

        import time

        duration = time.time() - self.start_time
        status = "completed" if success else "failed"

        self.logger.info(
            f"Operation {self.operation} {status} in {duration:.3f} seconds"
        )

        self.start_time = None


# 컨텍스트와 함께 로깅
def log_with_context(**context):
    """Decorator to add context to all log messages in a function"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with LogContext(**context):
                return func(*args, **kwargs)

        return wrapper

    return decorator


# 비동기 함수용 컨텍스트 로깅
def async_log_with_context(**context):
    """Decorator to add context to all log messages in an async function"""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            with LogContext(**context):
                return await func(*args, **kwargs)

        return wrapper

    return decorator
