"""Tests for URL detection and youtube.py helpers."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from localmeetingtranscriber.youtube import (
    is_url,
    is_direct_media_url,
    download_url_audio,
)


# ---------------------------------------------------------------------------
# is_url
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text, expected", [
    ("https://www.youtube.com/watch?v=abc", True),
    ("http://example.com/video.mp4", True),
    ("https://vimeo.com/123456", True),
    ("/local/path/file.m4a", False),
    ("./relative/file.mp4", False),
    ("ftp://not-http.com/file", False),
    ("", False),
])
def test_is_url(text, expected):
    assert is_url(text) == expected


# ---------------------------------------------------------------------------
# is_direct_media_url
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("url, expected", [
    ("https://cdn.example.com/meeting.mp4", True),
    ("https://cdn.example.com/meeting.mov", True),
    ("https://cdn.example.com/meeting.webm", True),
    ("https://cdn.example.com/meeting.mp4?token=abc", True),
    ("https://www.youtube.com/watch?v=abc", False),
    ("https://vimeo.com/123456", False),
    ("https://cdn.example.com/meeting.txt", False),
])
def test_is_direct_media_url(url, expected):
    assert is_direct_media_url(url) == expected


# ---------------------------------------------------------------------------
# download_url_audio — missing yt-dlp
# ---------------------------------------------------------------------------

def test_download_raises_import_error_without_yt_dlp(tmp_path):
    with patch.dict("sys.modules", {"yt_dlp": None}):
        with pytest.raises(ImportError, match="yt-dlp"):
            download_url_audio("https://example.com/video", tmp_path)


# ---------------------------------------------------------------------------
# download_url_audio — yt-dlp mocked
# ---------------------------------------------------------------------------

def _make_yt_dlp_mock(title="Test Video", filename="Test Video.m4a"):
    """Build a minimal yt_dlp mock that mimics YoutubeDL context-manager."""
    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = {"title": title}
    mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
    mock_ydl.__exit__ = MagicMock(return_value=False)

    mock_module = MagicMock()
    mock_module.YoutubeDL.return_value = mock_ydl
    return mock_module, mock_ydl


def test_download_returns_title(tmp_path):
    mock_module, mock_ydl = _make_yt_dlp_mock(title="My Meeting")

    # Create the expected output file so the fallback glob finds it
    (tmp_path / "My Meeting.m4a").touch()

    with patch.dict("sys.modules", {"yt_dlp": mock_module}):
        _, title = download_url_audio("https://youtube.com/watch?v=x", tmp_path)

    assert title == "My Meeting"


def test_download_creates_dest_dir(tmp_path):
    dest = tmp_path / "subdir"
    mock_module, _ = _make_yt_dlp_mock()
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "Test Video.m4a").touch()

    with patch.dict("sys.modules", {"yt_dlp": mock_module}):
        download_url_audio("https://youtube.com/watch?v=x", dest)

    assert dest.exists()


def test_download_progress_callback(tmp_path):
    mock_module, mock_ydl = _make_yt_dlp_mock()
    (tmp_path / "Test Video.m4a").touch()

    captured: list[float] = []

    # Simulate progress hook being called
    def fake_ydl_init(opts):
        hooks = opts.get("progress_hooks", [])
        for hook in hooks:
            hook({"status": "downloading", "downloaded_bytes": 50, "total_bytes": 100})
            hook({"status": "finished", "filename": str(tmp_path / "Test Video.m4a")})
        return mock_module.YoutubeDL.return_value

    mock_module.YoutubeDL.side_effect = fake_ydl_init

    with patch.dict("sys.modules", {"yt_dlp": mock_module}):
        download_url_audio(
            "https://youtube.com/watch?v=x",
            tmp_path,
            on_progress=captured.append,
        )

    assert any(0 < p <= 1.0 for p in captured)
