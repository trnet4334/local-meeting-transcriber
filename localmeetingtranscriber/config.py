"""Configuration loader for LocalMeetingTranscriber."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULTS: dict[str, Any] = {
    "ffmpeg_path": "ffmpeg",
    "whisper_cpp_path": "./whisper.cpp/main",
    "whisper_model_path": "./models/ggml-large-v3-q5_0.bin",
    "ollama_model": "qwen2.5:7b-instruct-q4_K_M",
    "output_dir": "./output_docx",
    "last_mode": 1,
}


def load_config(config_path: Path) -> dict[str, Any]:
    """Load config from JSON, merged onto defaults."""
    if not config_path.exists():
        return DEFAULTS.copy()

    data = json.loads(config_path.read_text(encoding="utf-8"))
    cfg = DEFAULTS.copy()
    cfg.update(data)
    return cfg


def merge_overrides(config: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    """Return a new config dict with non-None overrides applied."""
    merged = config.copy()
    for key, value in overrides.items():
        if value is not None:
            merged[key] = value
    return merged


def save_config(config_path: Path, config: dict[str, Any]) -> None:
    """Persist config to JSON (writes a new file, never mutates in-place)."""
    config_path.write_text(
        json.dumps(config, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
