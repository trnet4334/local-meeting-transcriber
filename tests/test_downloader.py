"""Tests for ModelDownloader (no real network access)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from localmeetingtranscriber.gui.downloader import ModelDownloader


def test_downloader_cancel_before_start(tmp_path):
    """cancel() before start() should not raise."""
    dl = ModelDownloader("http://example.com/model.bin", tmp_path / "model.bin")
    dl.cancel()  # no-op, must not raise
    assert not dl.isRunning()


def test_downloader_emits_error_on_bad_url(qtbot, tmp_path):
    """A bogus URL should cause the error signal to fire."""
    dest = tmp_path / "model.bin"
    dl = ModelDownloader("http://127.0.0.1:1/nonexistent.bin", dest)
    errors: list[str] = []
    dl.error.connect(errors.append)

    with qtbot.waitSignal(dl.error, timeout=5000):
        dl.start()

    assert errors
    assert not dest.exists()


def test_downloader_cancel_removes_partial_file(qtbot, tmp_path):
    """Cancellation must delete any partially-written file."""
    dest = tmp_path / "model.bin"

    # Patch urlopen to return a slow infinite stream
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.headers = {"Content-Length": "1000000"}
    # Each read returns 1 byte so we can cancel quickly
    mock_resp.read = MagicMock(return_value=b"\x00" * 64)

    with patch("localmeetingtranscriber.gui.downloader.urllib.request.urlopen", return_value=mock_resp):
        dl = ModelDownloader("http://example.com/model.bin", dest)
        dl.start()
        dl.cancel()
        dl.wait(3000)

    assert not dest.exists()
