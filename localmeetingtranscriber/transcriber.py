"""Transcription utilities using whisper.cpp."""
from __future__ import annotations

import subprocess
from pathlib import Path


def build_whisper_cmd(
    whisper_cpp_path: str, model_path: str, wav_path: str, output_base: str
) -> list[str]:
    """Build whisper.cpp command to output SRT."""
    return [
        whisper_cpp_path,
        "-m",
        model_path,
        "-f",
        wav_path,
        "--output-srt",
        "-of",
        output_base,
    ]


def transcribe_to_srt(
    whisper_cpp_path: str, model_path: Path, wav_path: Path, output_base: Path
) -> Path:
    """Run whisper.cpp to generate an SRT file.

    Stderr is captured so that diagnostic output is available via
    CalledProcessError.stderr on failure instead of polluting the terminal.
    """
    cmd = build_whisper_cmd(
        whisper_cpp_path, str(model_path), str(wav_path), str(output_base)
    )
    subprocess.run(cmd, check=True, capture_output=True)
    return output_base.with_suffix(".srt")
