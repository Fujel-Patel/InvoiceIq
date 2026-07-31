from __future__ import annotations

import logging
import sys

from loguru import logger


def setup_logging() -> None:
    """Configure loguru for the application."""
    logger.remove()

    logger.add(
        sys.stderr,
        colorize=True,
        level="INFO",
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        backtrace=True,
        diagnose=True,
    )

    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="7 days",
        serialize=True,
        level="DEBUG",
        backtrace=True,
        diagnose=True,
    )

    for noisy in ("uvicorn.access", "asyncpg", "httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
