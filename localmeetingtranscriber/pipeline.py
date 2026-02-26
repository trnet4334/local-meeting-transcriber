"""Shared pipeline orchestration for LocalMeetingTranscriber.

Both the CLI (main.py) and GUI (gui/worker.py) import from here.
"""
from __future__ import annotations

import shutil
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from localmeetingtranscriber.converter import convert_to_wav
from localmeetingtranscriber.exporter import build_output_path, export_docx
from localmeetingtranscriber.llm_polisher import polish_text
from localmeetingtranscriber.postprocess import srt_to_lines, strip_timestamps
from localmeetingtranscriber.transcriber import transcribe_to_srt

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ProgressCallback = Callable[[str], None]


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def resolve_file_path(path_str: str) -> Path:
    """Resolve a path, treating relative paths as project-root relative."""
    path = Path(path_str).expanduser()
    if not path.is_absolute():
        path = (PROJECT_ROOT / path).resolve()
    return path


def resolve_optional_exe(path_str: str) -> str:
    """Resolve an executable path only when it looks like a relative file path."""
    path = Path(path_str)
    if path.name != path_str:
        return str(resolve_file_path(path_str))
    return path_str


def check_command_exists(cmd: str) -> bool:
    """Return True if *cmd* is found on PATH."""
    return shutil.which(cmd) is not None


# ---------------------------------------------------------------------------
# Dependency validation
# ---------------------------------------------------------------------------

def mode_requires_ollama(mode: int) -> bool:
    """Return True if the selected mode requires Ollama."""
    return mode in (3, 4)


def validate_dependencies(config: dict[str, Any], mode: int) -> None:
    """Validate required external dependencies.

    Raises RuntimeError with a human-readable message if any dependency
    is missing.
    """
    ffmpeg_path = config["ffmpeg_path"]
    whisper_cpp_path = resolve_file_path(config["whisper_cpp_path"])
    whisper_model_path = resolve_file_path(config["whisper_model_path"])

    if Path(ffmpeg_path).name == ffmpeg_path and not check_command_exists(ffmpeg_path):
        raise RuntimeError("ffmpeg not found. Install ffmpeg or update config.")

    if not whisper_cpp_path.exists():
        raise RuntimeError(
            f"whisper.cpp binary not found at {whisper_cpp_path}. Update config path."
        )

    if not whisper_model_path.exists():
        raise RuntimeError(
            f"whisper.cpp model not found at {whisper_model_path}. Update config path."
        )

    if mode_requires_ollama(mode) and not check_command_exists("ollama"):
        raise RuntimeError("Ollama not found. Install Ollama for polishing modes.")


# ---------------------------------------------------------------------------
# Pipeline data model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PipelineInput:
    """All inputs needed to process a single audio file through the pipeline."""

    file_path: Path
    title: str
    date: str
    mode: int          # 1 = timestamps, 2 = clean, 3 = polished, 4 = polished+appendix
    config: dict[str, Any]
    output_dir: Path


# ---------------------------------------------------------------------------
# Pipeline execution
# ---------------------------------------------------------------------------

def _to_traditional(text: str) -> str:
    """Convert Simplified Chinese → Traditional Chinese (Taiwan) via OpenCC.

    Whisper outputs Simplified Chinese even for Traditional Chinese audio.
    Uses the ``s2twp`` config which handles phrase-level conversions
    (e.g. 软件→軟體, 内存→記憶體).  Silently skips if OpenCC is unavailable.
    """
    try:
        import opencc  # opencc-python-reimplemented
        return opencc.OpenCC("s2twp").convert(text)
    except Exception:
        return text


def _build_polish_prompt(clean_lines: list[str]) -> str:
    return (
        "You are a professional meeting assistant. "
        "Polish the transcript for clarity, remove filler words, "
        "fix punctuation, and keep meaning. Preserve Chinese text.\n\n"
        f"Transcript:\n{chr(10).join(clean_lines)}\n"
    )


def run_pipeline(
    pipeline_input: PipelineInput,
    on_progress: ProgressCallback | None = None,
) -> Path:
    """Run the full transcription pipeline for one audio file.

    Emits human-readable progress messages via *on_progress* (if provided).
    Returns the path to the generated DOCX file.
    Raises RuntimeError or subprocess.CalledProcessError on failure.
    """
    inp = pipeline_input

    def _emit(msg: str) -> None:
        if on_progress:
            on_progress(msg)

    inp.output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        wav_path = tmp_path / f"{inp.file_path.stem}.wav"
        output_base = tmp_path / inp.file_path.stem

        _emit("Converting to WAV...")
        convert_to_wav(
            resolve_optional_exe(inp.config["ffmpeg_path"]),
            inp.file_path,
            wav_path,
        )

        _emit("Transcribing with whisper.cpp...")
        srt_path = transcribe_to_srt(
            str(resolve_file_path(inp.config["whisper_cpp_path"])),
            resolve_file_path(inp.config["whisper_model_path"]),
            wav_path,
            output_base,
        )

        _emit("Post-processing transcript...")
        srt_text = srt_path.read_text(encoding="utf-8")
        srt_text = _to_traditional(srt_text)
        raw_lines = srt_to_lines(srt_text)
        clean_lines = strip_timestamps(raw_lines)

        if inp.mode == 1:
            final_lines = raw_lines
            appendix = None
        elif inp.mode == 2:
            final_lines = clean_lines
            appendix = None
        elif inp.mode == 3:
            _emit("Polishing transcript with Ollama...")
            polished = polish_text(
                inp.config["ollama_model"],
                _build_polish_prompt(clean_lines),
            )
            final_lines = polished.splitlines()
            appendix = None
        else:  # mode == 4
            _emit("Polishing transcript with Ollama...")
            polished = polish_text(
                inp.config["ollama_model"],
                _build_polish_prompt(clean_lines),
            )
            final_lines = polished.splitlines()
            appendix = raw_lines

        output_path = build_output_path(inp.output_dir, inp.title)
        _emit(f"Exporting DOCX to {output_path.name}...")
        export_docx(output_path, inp.title, inp.date, final_lines, appendix=appendix)
        _emit(f"Done: {output_path.name}")

    return output_path
