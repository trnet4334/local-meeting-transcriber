"""Tests for transcriber utilities."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from localmeetingtranscriber.transcriber import (
    build_whisper_cmd,
    detect_whisper_type,
    transcribe_to_srt,
)


# ---------------------------------------------------------------------------
# build_whisper_cmd
# ---------------------------------------------------------------------------

def test_build_whisper_cmd():
    cmd = build_whisper_cmd("./whisper.cpp/main", "model.bin", "audio.wav", "out")
    assert "--output-srt" in cmd
    assert "-m" in cmd
    assert "model.bin" in cmd
    assert "-f" in cmd
    assert "audio.wav" in cmd


# ---------------------------------------------------------------------------
# detect_whisper_type
# ---------------------------------------------------------------------------

def _make_run_result(stdout="", stderr="", returncode=0):
    from unittest.mock import MagicMock
    r = MagicMock()
    r.stdout = stdout
    r.stderr = stderr
    r.returncode = returncode
    return r


def test_detect_returns_whisper_cpp_from_stdout():
    result = _make_run_result(stdout="usage: main ... --output-srt ...")
    with patch("localmeetingtranscriber.transcriber.subprocess.run", return_value=result):
        detect_whisper_type.cache_clear()
        assert detect_whisper_type("/fake/whisper.cpp/main") == "whisper.cpp"


def test_detect_returns_openai_whisper_from_stdout():
    result = _make_run_result(stdout="usage: whisper ... --output_format {txt,vtt,srt}")
    with patch("localmeetingtranscriber.transcriber.subprocess.run", return_value=result):
        detect_whisper_type.cache_clear()
        assert detect_whisper_type("/usr/local/bin/whisper") == "openai-whisper"


def test_detect_returns_unknown_on_exception():
    with patch(
        "localmeetingtranscriber.transcriber.subprocess.run",
        side_effect=FileNotFoundError,
    ):
        detect_whisper_type.cache_clear()
        assert detect_whisper_type("/nonexistent/binary") == "unknown"


# ---------------------------------------------------------------------------
# transcribe_to_srt — error on openai-whisper
# ---------------------------------------------------------------------------

def test_transcribe_raises_on_openai_whisper(tmp_path):
    """transcribe_to_srt must raise RuntimeError if binary is openai-whisper."""
    result = _make_run_result(stdout="--output_format {txt,vtt,srt}")
    with patch("localmeetingtranscriber.transcriber.subprocess.run", return_value=result):
        detect_whisper_type.cache_clear()
        with pytest.raises(RuntimeError, match="openai-whisper"):
            transcribe_to_srt(
                "/usr/local/bin/whisper",
                tmp_path / "model.bin",
                tmp_path / "audio.wav",
                tmp_path / "audio",
            )
