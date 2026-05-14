"""Logging configuration for the newsletter agent."""

import logging
import sys
from pathlib import Path

_APP_LOGGER = "personal_rss_newsletter_agent"
_LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s — %(message)s"
_configured = False


def configure_logging(log_file: Path | None) -> None:
    """Configure logging for the application.

    Without log_file: INFO+ from app loggers goes to stdout.
    With log_file: same to stdout + DEBUG+ to file.
    Safe to call multiple times (idempotent).
    """
    global _configured
    if _configured:
        return
    _configured = True

    root = logging.getLogger()
    root.setLevel(logging.WARNING)

    app_logger = logging.getLogger(_APP_LOGGER)
    app_logger.setLevel(logging.DEBUG if log_file else logging.INFO)
    app_logger.propagate = False

    formatter = logging.Formatter(_LOG_FORMAT)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)
    app_logger.addHandler(stdout_handler)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        app_logger.addHandler(file_handler)
