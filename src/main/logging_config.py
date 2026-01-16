"""Logging configuration for the application."""

import logging
import sys
from typing import Any

from src.main.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """Configure structured logging for the application."""
    # Create formatter
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "%(funcName)s:%(lineno)d - %(message)s"
    )
    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.debug else logging.WARNING,
    )

    # Log startup message
    root_logger.info(f"Logging configured - Debug mode: {settings.debug}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module.

    Args:
        name: Name of the logger (typically __name__).

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)
