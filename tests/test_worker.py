"""Tests for the PipelineWorker QThread."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from localmeetingtranscriber.gui.worker import PipelineWorker
from localmeetingtranscriber.pipeline import PipelineInput

_CONFIG = {
    "ffmpeg_path": "ffmpeg",
    "whisper_cpp_path": "./whisper.cpp/main",
    "whisper_model_path": "./models/ggml-large-v3-q5_0.bin",
    "ollama_model": "qwen2.5:7b-instruct-q4_K_M",
}


def _make_inputs(tmp_path: Path, n: int = 1) -> list[PipelineInput]:
    inputs = []
    for i in range(n):
        f = tmp_path / f"meeting{i}.m4a"
        f.touch()
        inputs.append(
            PipelineInput(
                file_path=f,
                title=f"Meeting {i}",
                date="2026-02-26",
                mode=1,
                config=_CONFIG,
                output_dir=tmp_path / "output",
            )
        )
    return inputs


def test_worker_emits_pipeline_finished(qtbot, tmp_path):
    """Worker emits pipeline_finished after processing all inputs."""
    inputs = _make_inputs(tmp_path)
    worker = PipelineWorker(inputs)

    with patch(
        "localmeetingtranscriber.gui.worker.run_pipeline",
        return_value=tmp_path / "out.docx",
    ):
        with qtbot.waitSignal(worker.pipeline_finished, timeout=5000):
            worker.start()


def test_worker_emits_file_started_and_completed(qtbot, tmp_path):
    """Worker emits file_started then file_completed for each input."""
    inputs = _make_inputs(tmp_path, n=2)
    worker = PipelineWorker(inputs)
    started: list[str] = []
    completed: list[int] = []

    worker.file_started.connect(lambda i, name: started.append(name))
    worker.file_completed.connect(lambda i, _path: completed.append(i))

    with patch(
        "localmeetingtranscriber.gui.worker.run_pipeline",
        return_value=tmp_path / "out.docx",
    ):
        with qtbot.waitSignal(worker.pipeline_finished, timeout=5000):
            worker.start()

    assert len(started) == 2
    assert len(completed) == 2


def test_worker_emits_error_on_exception(qtbot, tmp_path):
    """Worker emits error_occurred (not pipeline_finished) when run_pipeline raises."""
    inputs = _make_inputs(tmp_path)
    worker = PipelineWorker(inputs)

    with patch(
        "localmeetingtranscriber.gui.worker.run_pipeline",
        side_effect=RuntimeError("boom"),
    ):
        with qtbot.waitSignal(worker.error_occurred, timeout=5000) as blocker:
            worker.start()

    assert "boom" in blocker.args[0]


def test_worker_cancel_prevents_subsequent_files(qtbot, tmp_path):
    """Cancelling after the first file prevents remaining files from running."""
    inputs = _make_inputs(tmp_path, n=3)
    worker = PipelineWorker(inputs)
    completed: list[int] = []
    worker.file_completed.connect(lambda i, _: completed.append(i))

    def slow_pipeline(inp, on_progress=None):
        # cancel immediately after the first call
        worker.cancel()
        return tmp_path / "out.docx"

    with patch(
        "localmeetingtranscriber.gui.worker.run_pipeline",
        side_effect=slow_pipeline,
    ):
        worker.start()
        worker.wait(3000)

    # Only the first file should have completed before cancellation took effect
    assert len(completed) <= 1


def test_worker_emits_log_messages(qtbot, tmp_path):
    """Progress callback emissions appear as log_message signals."""
    inputs = _make_inputs(tmp_path)
    worker = PipelineWorker(inputs)
    log_msgs: list[str] = []
    worker.log_message.connect(log_msgs.append)

    def pipeline_with_progress(inp, on_progress=None):
        if on_progress:
            on_progress("Step A")
            on_progress("Step B")
        return tmp_path / "out.docx"

    with patch(
        "localmeetingtranscriber.gui.worker.run_pipeline",
        side_effect=pipeline_with_progress,
    ):
        with qtbot.waitSignal(worker.pipeline_finished, timeout=5000):
            worker.start()

    assert "Step A" in log_msgs
    assert "Step B" in log_msgs
