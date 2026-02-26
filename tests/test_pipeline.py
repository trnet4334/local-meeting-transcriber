"""Tests for the shared pipeline orchestration module."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from localmeetingtranscriber.pipeline import (
    PipelineInput,
    mode_requires_ollama,
    run_pipeline,
    validate_dependencies,
    resolve_file_path,
    PROJECT_ROOT,
)

_CONFIG = {
    "ffmpeg_path": "ffmpeg",
    "whisper_cpp_path": "./whisper.cpp/main",
    "whisper_model_path": "./models/ggml-large-v3-q5_0.bin",
    "ollama_model": "qwen2.5:7b-instruct-q4_K_M",
}

_SRT = "1\n00:00:01,000 --> 00:00:02,000\nHello world\n\n"


def _make_input(tmp_path: Path, mode: int = 1) -> PipelineInput:
    audio = tmp_path / "meeting.m4a"
    audio.touch()
    return PipelineInput(
        file_path=audio,
        title="Test Meeting",
        date="2026-02-26",
        mode=mode,
        config=_CONFIG,
        output_dir=tmp_path / "output",
    )


def _fake_transcribe(whisper_path, model_path, wav_path, output_base):
    """Write a minimal SRT file and return its path."""
    srt = output_base.with_suffix(".srt")
    srt.parent.mkdir(parents=True, exist_ok=True)
    srt.write_text(_SRT, encoding="utf-8")
    return srt


# ---------------------------------------------------------------------------
# mode_requires_ollama
# ---------------------------------------------------------------------------

def test_mode_requires_ollama_false_for_1_2():
    assert mode_requires_ollama(1) is False
    assert mode_requires_ollama(2) is False


def test_mode_requires_ollama_true_for_3_4():
    assert mode_requires_ollama(3) is True
    assert mode_requires_ollama(4) is True


# ---------------------------------------------------------------------------
# resolve_file_path
# ---------------------------------------------------------------------------

def test_resolve_file_path_absolute_unchanged(tmp_path):
    result = resolve_file_path(str(tmp_path))
    assert result == tmp_path


def test_resolve_file_path_relative_anchored_to_project_root():
    result = resolve_file_path("./some/path")
    assert result == (PROJECT_ROOT / "some/path").resolve()


# ---------------------------------------------------------------------------
# validate_dependencies
# ---------------------------------------------------------------------------

def test_validate_dependencies_raises_when_ffmpeg_missing():
    with patch("localmeetingtranscriber.pipeline.check_command_exists", return_value=False):
        with pytest.raises(RuntimeError, match="ffmpeg"):
            validate_dependencies(_CONFIG, mode=1)


def test_validate_dependencies_raises_when_whisper_binary_missing(tmp_path):
    cfg = {**_CONFIG, "whisper_cpp_path": str(tmp_path / "nonexistent")}
    with patch("localmeetingtranscriber.pipeline.check_command_exists", return_value=True):
        with pytest.raises(RuntimeError, match="whisper.cpp binary"):
            validate_dependencies(cfg, mode=1)


def test_validate_dependencies_raises_for_ollama_mode_without_ollama(tmp_path):
    whisper_bin = tmp_path / "whisper"
    whisper_bin.touch()
    model = tmp_path / "model.bin"
    model.touch()
    cfg = {
        **_CONFIG,
        "whisper_cpp_path": str(whisper_bin),
        "whisper_model_path": str(model),
    }

    def fake_which(cmd):
        return None if cmd == "ollama" else "/usr/bin/ffmpeg"

    with patch("localmeetingtranscriber.pipeline.check_command_exists", side_effect=fake_which):
        with pytest.raises(RuntimeError, match="Ollama"):
            validate_dependencies(cfg, mode=3)


# ---------------------------------------------------------------------------
# run_pipeline — mode branching
# ---------------------------------------------------------------------------

def test_run_pipeline_mode1_returns_docx_path(tmp_path):
    inp = _make_input(tmp_path, mode=1)
    with (
        patch("localmeetingtranscriber.pipeline.convert_to_wav"),
        patch("localmeetingtranscriber.pipeline.transcribe_to_srt", side_effect=_fake_transcribe),
        patch("localmeetingtranscriber.pipeline.export_docx"),
    ):
        result = run_pipeline(inp)
    assert result.suffix == ".docx"
    assert result.parent == inp.output_dir


def test_run_pipeline_mode2_does_not_call_polish(tmp_path):
    inp = _make_input(tmp_path, mode=2)
    with (
        patch("localmeetingtranscriber.pipeline.convert_to_wav"),
        patch("localmeetingtranscriber.pipeline.transcribe_to_srt", side_effect=_fake_transcribe),
        patch("localmeetingtranscriber.pipeline.export_docx"),
        patch("localmeetingtranscriber.pipeline.polish_text") as mock_polish,
    ):
        run_pipeline(inp)
    mock_polish.assert_not_called()


def test_run_pipeline_mode3_calls_polish_once(tmp_path):
    inp = _make_input(tmp_path, mode=3)
    with (
        patch("localmeetingtranscriber.pipeline.convert_to_wav"),
        patch("localmeetingtranscriber.pipeline.transcribe_to_srt", side_effect=_fake_transcribe),
        patch("localmeetingtranscriber.pipeline.export_docx"),
        patch("localmeetingtranscriber.pipeline.polish_text", return_value="Polished text") as mock_polish,
    ):
        run_pipeline(inp)
    mock_polish.assert_called_once()


def test_run_pipeline_mode4_passes_appendix_to_exporter(tmp_path):
    inp = _make_input(tmp_path, mode=4)
    with (
        patch("localmeetingtranscriber.pipeline.convert_to_wav"),
        patch("localmeetingtranscriber.pipeline.transcribe_to_srt", side_effect=_fake_transcribe),
        patch("localmeetingtranscriber.pipeline.export_docx") as mock_export,
        patch("localmeetingtranscriber.pipeline.polish_text", return_value="Polished"),
    ):
        run_pipeline(inp)
    _, kwargs = mock_export.call_args
    assert kwargs.get("appendix") is not None


# ---------------------------------------------------------------------------
# run_pipeline — progress callback
# ---------------------------------------------------------------------------

def test_run_pipeline_calls_progress_callback(tmp_path):
    inp = _make_input(tmp_path, mode=2)
    messages: list[str] = []

    with (
        patch("localmeetingtranscriber.pipeline.convert_to_wav"),
        patch("localmeetingtranscriber.pipeline.transcribe_to_srt", side_effect=_fake_transcribe),
        patch("localmeetingtranscriber.pipeline.export_docx"),
    ):
        run_pipeline(inp, on_progress=messages.append)

    assert any("Converting" in m for m in messages)
    assert any("Transcribing" in m for m in messages)
    assert any("Exporting" in m for m in messages)
    assert any("Done" in m for m in messages)


def test_run_pipeline_no_callback_does_not_raise(tmp_path):
    inp = _make_input(tmp_path, mode=1)
    with (
        patch("localmeetingtranscriber.pipeline.convert_to_wav"),
        patch("localmeetingtranscriber.pipeline.transcribe_to_srt", side_effect=_fake_transcribe),
        patch("localmeetingtranscriber.pipeline.export_docx"),
    ):
        run_pipeline(inp, on_progress=None)  # must not raise
