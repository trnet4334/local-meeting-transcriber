# LocalMeetingTranscriber Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an interactive CLI that converts `.m4a` recordings into `.docx` meeting transcripts via `ffmpeg`, `whisper.cpp`, and optional Ollama polishing.

**Architecture:** Modular pipeline with `converter`, `transcriber`, `postprocess`, `llm_polisher`, and `exporter` modules orchestrated by a CLI entrypoint. Configurable binary/model paths via `config.json` plus CLI overrides.

**Tech Stack:** Python 3.11, `python-docx`, `subprocess`, `ffmpeg`, `whisper.cpp`, Ollama.

---

### Task 1: Create project layout and config loader

**Files:**
- Create: `localmeetingtranscriber/__init__.py`
- Create: `localmeetingtranscriber/config.py`
- Create: `config.json`
- Create: `requirements.txt`

**Step 1: Write the failing test**

```python
def test_config_loads_defaults(tmp_path, monkeypatch):
    # config.json missing -> defaults
    from localmeetingtranscriber.config import load_config
    cfg = load_config(config_path=tmp_path / "missing.json")
    assert "whisper_cpp_path" in cfg
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py::test_config_loads_defaults -v`
Expected: FAIL with `ModuleNotFoundError` or `ImportError`

**Step 3: Write minimal implementation**

```python
# localmeetingtranscriber/config.py
from __future__ import annotations
import json
from pathlib import Path

DEFAULTS = {
    "ffmpeg_path": "ffmpeg",
    "whisper_cpp_path": "./whisper.cpp/main",
    "whisper_model_path": "./models/ggml-large-v3-q5_0.bin",
    "ollama_model": "qwen2.5:7b-instruct-q4_K_M",
}

def load_config(config_path: Path) -> dict:
    if not config_path.exists():
        return DEFAULTS.copy()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    cfg = DEFAULTS.copy()
    cfg.update(data)
    return cfg
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py::test_config_loads_defaults -v`
Expected: PASS

**Step 5: Commit**

```bash
git add localmeetingtranscriber/__init__.py localmeetingtranscriber/config.py config.json requirements.txt tests/test_config.py
git commit -m "feat: add config loader and defaults"
```

---

### Task 2: Implement converter module (ffmpeg)

**Files:**
- Create: `localmeetingtranscriber/converter.py`
- Create: `tests/test_converter.py`

**Step 1: Write the failing test**

```python
def test_build_ffmpeg_cmd():
    from localmeetingtranscriber.converter import build_ffmpeg_cmd
    cmd = build_ffmpeg_cmd("ffmpeg", "in.m4a", "out.wav")
    assert cmd[:2] == ["ffmpeg", "-y"]
    assert "-ar" in cmd and "16000" in cmd
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_converter.py::test_build_ffmpeg_cmd -v`
Expected: FAIL with `ImportError`

**Step 3: Write minimal implementation**

```python
# localmeetingtranscriber/converter.py
from __future__ import annotations
import subprocess
from pathlib import Path


def build_ffmpeg_cmd(ffmpeg_path: str, input_path: str, output_path: str) -> list[str]:
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
    cmd = build_ffmpeg_cmd(ffmpeg_path, str(input_path), str(output_path))
    subprocess.run(cmd, check=True, capture_output=True)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_converter.py::test_build_ffmpeg_cmd -v`
Expected: PASS

**Step 5: Commit**

```bash
git add localmeetingtranscriber/converter.py tests/test_converter.py
git commit -m "feat: add ffmpeg conversion helper"
```

---

### Task 3: Implement transcriber module (whisper.cpp)

**Files:**
- Create: `localmeetingtranscriber/transcriber.py`
- Create: `tests/test_transcriber.py`

**Step 1: Write the failing test**

```python
def test_build_whisper_cmd():
    from localmeetingtranscriber.transcriber import build_whisper_cmd
    cmd = build_whisper_cmd("./whisper.cpp/main", "model.bin", "audio.wav", "out")
    assert "--output-srt" in cmd
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_transcriber.py::test_build_whisper_cmd -v`
Expected: FAIL with `ImportError`

**Step 3: Write minimal implementation**

```python
# localmeetingtranscriber/transcriber.py
from __future__ import annotations
import subprocess
from pathlib import Path


def build_whisper_cmd(whisper_cpp_path: str, model_path: str, wav_path: str, output_base: str) -> list[str]:
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


def transcribe_to_srt(whisper_cpp_path: str, model_path: Path, wav_path: Path, output_base: Path) -> Path:
    cmd = build_whisper_cmd(whisper_cpp_path, str(model_path), str(wav_path), str(output_base))
    subprocess.run(cmd, check=True, capture_output=True)
    return output_base.with_suffix(".srt")
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_transcriber.py::test_build_whisper_cmd -v`
Expected: PASS

**Step 5: Commit**

```bash
git add localmeetingtranscriber/transcriber.py tests/test_transcriber.py
git commit -m "feat: add whisper.cpp invocation"
```

---

### Task 4: Implement postprocess (SRT parsing + timestamp stripping)

**Files:**
- Create: `localmeetingtranscriber/postprocess.py`
- Create: `tests/test_postprocess.py`

**Step 1: Write the failing test**

```python
def test_srt_to_lines():
    from localmeetingtranscriber.postprocess import srt_to_lines
    srt = "1\n00:00:00,000 --> 00:00:02,000\nHello world\n"
    lines = srt_to_lines(srt)
    assert lines[0].startswith("[00:00:00]")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_postprocess.py::test_srt_to_lines -v`
Expected: FAIL with `ImportError`

**Step 3: Write minimal implementation**

```python
# localmeetingtranscriber/postprocess.py
from __future__ import annotations
import re

TIME_RE = re.compile(r"(\d\d):(\d\d):(\d\d),\d\d\d")


def srt_to_lines(srt_text: str) -> list[str]:
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
    return [re.sub(r"^\[\d\d:\d\d:\d\d\]\s*", "", line) for line in lines]
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_postprocess.py::test_srt_to_lines -v`
Expected: PASS

**Step 5: Commit**

```bash
git add localmeetingtranscriber/postprocess.py tests/test_postprocess.py
git commit -m "feat: add srt parsing and timestamp stripping"
```

---

### Task 5: Implement Ollama polisher

**Files:**
- Create: `localmeetingtranscriber/llm_polisher.py`
- Create: `tests/test_llm_polisher.py`

**Step 1: Write the failing test**

```python
def test_build_ollama_cmd():
    from localmeetingtranscriber.llm_polisher import build_ollama_cmd
    cmd = build_ollama_cmd("qwen2.5:7b-instruct-q4_K_M")
    assert cmd[:2] == ["ollama", "run"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_llm_polisher.py::test_build_ollama_cmd -v`
Expected: FAIL with `ImportError`

**Step 3: Write minimal implementation**

```python
# localmeetingtranscriber/llm_polisher.py
from __future__ import annotations
import subprocess


def build_ollama_cmd(model: str) -> list[str]:
    return ["ollama", "run", model]


def polish_text(model: str, text: str) -> str:
    cmd = build_ollama_cmd(model)
    proc = subprocess.run(cmd, input=text.encode("utf-8"), check=True, capture_output=True)
    return proc.stdout.decode("utf-8").strip()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_llm_polisher.py::test_build_ollama_cmd -v`
Expected: PASS

**Step 5: Commit**

```bash
git add localmeetingtranscriber/llm_polisher.py tests/test_llm_polisher.py
git commit -m "feat: add ollama polisher"
```

---

### Task 6: Implement DOCX exporter

**Files:**
- Create: `localmeetingtranscriber/exporter.py`
- Create: `tests/test_exporter.py`

**Step 1: Write the failing test**

```python
def test_build_docx_path(tmp_path):
    from localmeetingtranscriber.exporter import build_output_path
    path = build_output_path(tmp_path, "Meeting")
    assert str(path).endswith("Meeting.docx")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_exporter.py::test_build_docx_path -v`
Expected: FAIL with `ImportError`

**Step 3: Write minimal implementation**

```python
# localmeetingtranscriber/exporter.py
from __future__ import annotations
from pathlib import Path
from docx import Document


def build_output_path(output_dir: Path, title: str) -> Path:
    safe_title = " ".join(title.strip().split())
    return output_dir / f"{safe_title}.docx"


def export_docx(output_path: Path, title: str, date: str, lines: list[str], appendix: list[str] | None = None) -> None:
    doc = Document()
    doc.add_heading(title, level=1)
    doc.add_paragraph(f"Date: {date}")
    doc.add_paragraph("")
    for line in lines:
        doc.add_paragraph(line)
    if appendix:
        doc.add_page_break()
        doc.add_heading("Appendix: Raw Transcript", level=2)
        for line in appendix:
            doc.add_paragraph(line)
    doc.save(output_path)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_exporter.py::test_build_docx_path -v`
Expected: PASS

**Step 5: Commit**

```bash
git add localmeetingtranscriber/exporter.py tests/test_exporter.py
git commit -m "feat: add docx export"
```

---

### Task 7: Implement CLI (main pipeline)

**Files:**
- Create: `localmeetingtranscriber/main.py`
- Create: `tests/test_cli_helpers.py`

**Step 1: Write the failing test**

```python
def test_parse_selection():
    from localmeetingtranscriber.main import parse_selection
    assert parse_selection("1,3", 5) == [0, 2]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli_helpers.py::test_parse_selection -v`
Expected: FAIL with `ImportError`

**Step 3: Write minimal implementation**

```python
# localmeetingtranscriber/main.py
from __future__ import annotations
from pathlib import Path


def parse_selection(raw: str, max_count: int) -> list[int]:
    indices: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            num = int(part)
        except ValueError:
            raise ValueError(f"Invalid selection '{part}': expected a number")
        if num < 1 or num > max_count:
            raise ValueError(f"Selection {num} out of range (1–{max_count})")
        indices.append(num - 1)
    return sorted(set(indices))
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli_helpers.py::test_parse_selection -v`
Expected: PASS

**Step 5: Commit**

```bash
git add localmeetingtranscriber/main.py tests/test_cli_helpers.py
git commit -m "feat: add cli helpers"
```

---

### Task 8: Wire full pipeline and documentation

**Files:**
- Modify: `localmeetingtranscriber/main.py`
- Modify: `config.json`
- Create: `README.md`
- Create: `input_audio/.gitkeep`
- Create: `output_docx/.gitkeep`

**Step 1: Write the failing test**

```python
def test_mode_requires_ollama():
    from localmeetingtranscriber.main import mode_requires_ollama
    assert mode_requires_ollama(3) is True
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli_helpers.py::test_mode_requires_ollama -v`
Expected: FAIL with `ImportError`

**Step 3: Write minimal implementation**

```python
# localmeetingtranscriber/main.py

def mode_requires_ollama(mode: int) -> bool:
    return mode in (3, 4)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli_helpers.py::test_mode_requires_ollama -v`
Expected: PASS

**Step 5: Commit**

```bash
git add localmeetingtranscriber/main.py tests/test_cli_helpers.py README.md config.json input_audio/.gitkeep output_docx/.gitkeep
git commit -m "feat: wire pipeline and add docs"
```

---

### Task 9: Full test run

**Files:**
- None

**Step 1: Run tests**

Run: `pytest -v`
Expected: All tests PASS

**Step 2: Commit (if needed)**

```bash
git add -A
git commit -m "test: green suite"
```
