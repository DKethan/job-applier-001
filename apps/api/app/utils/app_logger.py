import os
from loguru import logger as loguru_logger
from typing import Any

# Define log file path relative to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "app.log")

# Ensure the logs directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Determine log format based on environment
environment = os.getenv("APP_ENV", "local").lower()

# Configure Loguru Logger with environment-specific settings
if environment in ["prod", "production"]:
    # JSON format for production (better for log aggregation and monitoring)
    loguru_logger.add(
        LOG_FILE,
        rotation="1 day",
        retention="30 days",  # Keep logs longer in production
        format="{time:YYYY-MM-DDTHH:mm:ss}Z | {level} | {file}:{name}:{line} | {message} | {extra}",
        level="INFO",
        serialize=True,  # Enable JSON serialization
    )
else:
    # Human-readable colored format for development
    loguru_logger.add(
        LOG_FILE,
        rotation="1 day",
        retention="10 days",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan> | "
               "<cyan>{file}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG",
    )


class AppLogger:
    """Logging class using Loguru for structured logging. Provides synchronous and asynchronous logging capabilities."""

    def __init__(self) -> None:
        pass

    def log_info(self, *args: Any, **kwargs: Any) -> None:
        """Logs an info message."""
        level = kwargs.pop("level", "INFO")
        message = " ".join(map(str, args))
        loguru_logger.opt(depth=1).log(level, message, **kwargs)

    async def async_log_info(self, *args: Any, **kwargs: Any) -> None:
        """Logs an info message asynchronously."""
        level = kwargs.pop("level", "INFO")
        message = " ".join(map(str, args))
        loguru_logger.opt(depth=1).log(level, message, **kwargs)

    def log_error(self, *args: Any, **kwargs: Any) -> None:
        """Logs an error message."""
        message = " ".join(map(str, args))
        loguru_logger.opt(depth=1).error(message, **kwargs)

    async def async_log_error(self, *args: Any, **kwargs: Any) -> None:
        """Logs an error message asynchronously."""
        message = " ".join(map(str, args))
        loguru_logger.opt(depth=1).error(message, **kwargs)

    def log_debug(self, *args: Any, **kwargs: Any) -> None:
        """Logs a debug message."""
        message = " ".join(map(str, args))
        loguru_logger.opt(depth=1).debug(message, **kwargs)

    async def async_log_debug(self, *args: Any, **kwargs: Any) -> None:
        """Logs a debug message asynchronously."""
        message = " ".join(map(str, args))
        loguru_logger.opt(depth=1).debug(message, **kwargs)

    def log_warning(self, *args: Any, **kwargs: Any) -> None:
        """Logs a warning message."""
        message = " ".join(map(str, args))
        loguru_logger.opt(depth=1).warning(message, **kwargs)

    async def async_log_warning(self, *args: Any, **kwargs: Any) -> None:
        """Logs a warning message asynchronously."""
        message = " ".join(map(str, args))
        loguru_logger.opt(depth=1).warning(message, **kwargs)


# Instantiate global logger instance
app_logger = AppLogger()