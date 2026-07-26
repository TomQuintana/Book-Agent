"""Logging setup for the ASTA application."""

import logging

from src.config.settings import settings


def setup_logging() -> None:
    """Configure the root logger's level and format."""
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.WARNING)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)
