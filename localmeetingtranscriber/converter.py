"""Audio conversion utilities."""
from __future__ import annotations

import subprocess
from pathlib import Path


def build_ffmpeg_cmd(ffmpeg_path: str, input_path: str, output_path: str) -> list[str]:
    """Build ffmpeg command to convert input audio to 16kHz mono WAV."""
    return [
        ffmpeg_path,
        "-y",
        "-i",
        input_path,
        "-ac",
        "1",
        "-ar",
        "16000",
        output_path,
    ]


def convert_to_wav(ffmpeg_path: str, input_path: Path, output_path: Path) -> None:
    """Convert an audio file to 16kHz mono WAV.

    Stderr is captured so that diagnostic output is available via
    CalledProcessError.stderr on failure instead of polluting the terminal.
    """
    cmd = build_ffmpeg_cmd(ffmpeg_path, str(input_path), str(output_path))
    subprocess.run(cmd, check=True, capture_output=True)
