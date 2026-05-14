"""Tests for logging_setup.configure_logging()."""

import logging

import pytest

from personal_rss_newsletter_agent.logging_setup import (
    _APP_LOGGER,
    configure_logging,
)


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging state and the idempotency guard between tests."""
    import personal_rss_newsletter_agent.logging_setup as ls

    yield

    app_logger = logging.getLogger(_APP_LOGGER)
    app_logger.handlers.clear()
    app_logger.propagate = True
    ls._configured = False


def test_no_log_file_adds_stream_handler_only(tmp_path):
    configure_logging(None)

    app_logger = logging.getLogger(_APP_LOGGER)
    handler_types = [type(h) for h in app_logger.handlers]

    assert logging.StreamHandler in handler_types
    assert logging.FileHandler not in handler_types


def test_log_file_adds_file_handler(tmp_path):
    log_path = tmp_path / "run.log"
    configure_logging(log_path)

    app_logger = logging.getLogger(_APP_LOGGER)
    file_handlers = [h for h in app_logger.handlers if isinstance(h, logging.FileHandler)]

    assert len(file_handlers) == 1


def test_log_file_is_created_on_first_log(tmp_path):
    log_path = tmp_path / "subdir" / "run.log"
    configure_logging(log_path)

    logging.getLogger(_APP_LOGGER).info("test message")

    assert log_path.exists()


def test_idempotent_when_called_twice(tmp_path):
    configure_logging(None)
    configure_logging(None)

    app_logger = logging.getLogger(_APP_LOGGER)
    assert len(app_logger.handlers) == 1


def test_no_log_file_sets_info_level():
    configure_logging(None)

    app_logger = logging.getLogger(_APP_LOGGER)
    assert app_logger.level == logging.INFO


def test_log_file_sets_debug_level(tmp_path):
    configure_logging(tmp_path / "run.log")

    app_logger = logging.getLogger(_APP_LOGGER)
    assert app_logger.level == logging.DEBUG
