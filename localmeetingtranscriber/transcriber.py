"""Transcription utilities using whisper.cpp."""
from __future__ import annotations

import functools
import subprocess
from pathlib import Path
from typing import Literal

WhisperBackend = Literal["whisper.cpp", "openai-whisper", "unknown"]


@functools.lru_cache(maxsize=16)
def detect_whisper_type(binary_path: str) -> WhisperBackend:
    """Detect whether *binary_path* is a whisper.cpp or openai-whisper binary.

    Result is cached per binary path so detection only runs once per session.
    """
    try:
        result = subprocess.run(
            [binary_path, "--help"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        combined = result.stdout + result.stderr
        if "--output-srt" in combined or "-of FNAME" in combined:
            return "whisper.cpp"
        if "--output_format" in combined or "--output_dir" in combined:
            return "openai-whisper"
    except Exception:
        pass
    return "unknown"


def build_whisper_cmd(
    whisper_cpp_path: str, model_path: str, wav_path: str, output_base: str
) -> list[str]:
    """Build a whisper.cpp command to write <output_base>.srt."""
    return [
        whisper_cpp_path,
        "-m", model_path,
        "-f", wav_path,
        "--output-srt",
        "-of", output_base,
    ]


def transcribe_to_srt(
    whisper_cpp_path: str, model_path: Path, wav_path: Path, output_base: Path
) -> Path:
    """Run whisper.cpp to generate an SRT file.

    Raises
    ------
    RuntimeError
        If the configured binary is openai-whisper instead of whisper.cpp.
    subprocess.CalledProcessError
        If whisper.cpp exits with a non-zero status.
    """
    backend = detect_whisper_type(whisper_cpp_path)
    if backend == "openai-whisper":
        raise RuntimeError(
            f"'{whisper_cpp_path}' is the openai-whisper Python package, "
            "not whisper.cpp.\n\n"
            "Please install and configure the whisper.cpp binary instead:\n"
            "  https://github.com/ggerganov/whisper.cpp"
        )

    cmd = build_whisper_cmd(
        whisper_cpp_path, str(model_path), str(wav_path), str(output_base)
    )
    subprocess.run(cmd, check=True, capture_output=True)
    return output_base.with_suffix(".srt")
