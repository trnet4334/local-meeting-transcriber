"""Local LLM polishing via Ollama."""
from __future__ import annotations

import subprocess


def build_ollama_cmd(model: str) -> list[str]:
    """Build the ollama command to run a model."""
    return ["ollama", "run", model]


def polish_text(model: str, text: str) -> str:
    """Polish text using a local Ollama model."""
    cmd = build_ollama_cmd(model)
    proc = subprocess.run(
        cmd,
        input=text.encode("utf-8"),
        check=True,
        capture_output=True,
    )
    return proc.stdout.decode("utf-8").strip()
