"""Shared pytest fixtures for all test modules."""
from __future__ import annotations

import os

import pytest

# Run Qt tests with an offscreen platform so they work headlessly in CI.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="session")
def qapp_args():
    """Provide minimal QApplication arguments for pytest-qt."""
    return ["LocalMeetingTranscriber-tests"]
