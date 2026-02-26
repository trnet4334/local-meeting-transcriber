"""Post-processing of SRT transcripts."""
from __future__ import annotations

import re

TIME_RE = re.compile(r"(\d\d):(\d\d):(\d\d),\d\d\d")


def srt_to_lines(srt_text: str) -> list[str]:
    """Convert SRT content to timestamped lines: [HH:MM:SS] text."""
    blocks = [b for b in srt_text.strip().split("\n\n") if b.strip()]
    lines: list[str] = []
    for block in blocks:
        parts = block.split("\n")
        if len(parts) < 3:
            continue
        time_line = parts[1]
        text = " ".join(parts[2:]).strip()
        match = TIME_RE.search(time_line)
        if not match:
            continue
        hh, mm, ss = match.groups()
        lines.append(f"[{hh}:{mm}:{ss}] {text}")
    return lines


def strip_timestamps(lines: list[str]) -> list[str]:
    """Remove leading [HH:MM:SS] timestamps from lines."""
    return [re.sub(r"^\[\d\d:\d\d:\d\d\]\s*", "", line) for line in lines]
