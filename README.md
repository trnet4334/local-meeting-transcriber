# LocalMeetingTranscriber

> 也有[繁體中文版說明](README.zh-TW.md)

A local, privacy-first desktop app that turns `.m4a` meeting recordings into polished Word (`.docx`) transcripts — entirely on your own machine, with no cloud uploads.

Built with Python + PySide6. Transcription via [whisper.cpp](https://github.com/ggerganov/whisper.cpp); optional AI polishing via [Ollama](https://ollama.ai).

---

## Features

- **Native macOS GUI** with scrollable, bilingual (English / 繁體中文) interface
- **First-launch setup wizard** — guides you through configuring whisper.cpp, downloading a model, and checking Ollama
- **Four output modes**:
  1. Full transcript with timestamps
  2. Clean transcript without timestamps
  3. Polished transcript (Ollama LLM)
  4. Polished transcript + raw appendix (Ollama LLM)
- **Traditional Chinese output** — whisper output is automatically converted from Simplified → Traditional Chinese (Taiwan) via OpenCC
- Batch processing — add multiple `.m4a` files at once with editable titles and dates
- Exports clean `.docx` files ready to share
- Settings persist across sessions (`config.json`)
- Also available as a CLI (`lmt`)

---

## Requirements

| Dependency | Purpose | Install |
|---|---|---|
| Python 3.11+ | Runtime | [python.org](https://www.python.org) |
| ffmpeg | Audio conversion | `brew install ffmpeg` |
| whisper.cpp | Speech-to-text | `brew install whisper-cpp` |
| Ollama | LLM polishing (modes 3 & 4 only) | [ollama.ai](https://ollama.ai) |

> **Note:** The app requires the **whisper.cpp** binary (`whisper-cli`), not the Python `openai-whisper` package. The setup wizard will detect and warn you if the wrong binary is configured.

---

## Quick Start

### 1. Install Python dependencies

```bash
git clone https://github.com/trnet4334/LocalMeetingTranscriber.git
cd LocalMeetingTranscriber
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Install system dependencies

```bash
# macOS (Homebrew)
brew install ffmpeg whisper-cpp

# Pull an Ollama model (only needed for modes 3 & 4)
ollama pull qwen2.5:7b-instruct-q4_K_M
```

### 3. Launch the GUI

```bash
python -m localmeetingtranscriber.gui.app
```

Or install as a command and run:

```bash
pip install -e ".[gui]"
lmt-gui
```

On first launch, the **Setup Wizard** will appear automatically to help you:
- Locate the `whisper-cli` binary
- Download a Whisper model (default: Small, ~466 MB)
- Check if Ollama is running

---

## Whisper Models

The wizard lets you choose from five models. Larger models are slower but more accurate:

| Model | Size | Accuracy | Recommended for |
|---|---|---|---|
| Tiny | ~75 MB | Basic | Quick drafts |
| Base | ~142 MB | Decent | Short meetings |
| **Small** | **~466 MB** | **Good** | **Default — good balance** |
| Medium | ~1.5 GB | Better | Longer meetings |
| Large-v3 Q5 | ~1.1 GB | Best | High-accuracy needs |

You can also install whisper-cpp via Homebrew and use the bundled `whisper-cli` binary directly:

```bash
brew install whisper-cpp
# Binary location: /usr/local/bin/whisper-cli
```

---

## GUI Overview

```
┌─────────────────────────────────────────────┐  Language: [English ▼]
│  Input Files                                │
│  ┌─────────────────────────────────────┐   │
│  │  meeting_2026-03-01.m4a             │   │
│  └─────────────────────────────────────┘   │
│  [Add Files…]  [Remove Selected]           │
│                                            │
│  Output                                    │
│  Mode:          [1. Full transcript… ▼]    │
│  Output Folder: /Users/…/Downloads [Browse]│
│                                            │
│  Dependencies                              │
│  ffmpeg:        ffmpeg                     │
│  whisper binary:/usr/local/bin/whisper-cli │
│  Whisper model: …/models/ggml-small.bin    │
│  Ollama model:  qwen2.5:7b-instruct-q4_K_M│
│                                            │
│  Meeting Metadata (editable)               │
│  ┌──────────┬────────────────┬──────────┐  │
│  │ File     │ Title          │ Date     │  │
│  └──────────┴────────────────┴──────────┘  │
│                                            │
│                [Start Processing] [Cancel] │
│  Progress ─────────────────────────────── │
│  Log ──────────────────────────────────── │
└────────────────────────────────────────────┘
```

---

## CLI Usage

A text-based CLI is also available for headless/server use:

```bash
# Run interactively
python -m localmeetingtranscriber.main

# Or via the installed command
lmt
```

The CLI will prompt for file selection, output mode, title, and date.

---

## Project Structure

```
LocalMeetingTranscriber/
├── localmeetingtranscriber/
│   ├── gui/
│   │   ├── app.py           # Entry point — setup wizard + MainWindow
│   │   ├── main_window.py   # Main GUI window
│   │   ├── worker.py        # QThread pipeline worker
│   │   ├── setup_wizard.py  # First-launch wizard
│   │   ├── downloader.py    # Model download thread
│   │   └── i18n.py          # EN / 繁體中文 translations
│   ├── pipeline.py          # Shared pipeline (CLI + GUI)
│   ├── transcriber.py       # whisper.cpp wrapper + backend detection
│   ├── converter.py         # ffmpeg WAV conversion
│   ├── postprocess.py       # SRT parsing
│   ├── exporter.py          # DOCX export
│   ├── llm_polisher.py      # Ollama integration
│   ├── config.py            # Config load/save
│   └── main.py              # CLI entry point
├── models/                  # Downloaded Whisper model files
├── tests/
├── config.json
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Configuration (`config.json`)

```json
{
  "ffmpeg_path": "ffmpeg",
  "whisper_cpp_path": "/usr/local/bin/whisper-cli",
  "whisper_model_path": "./models/ggml-small.bin",
  "ollama_model": "qwen2.5:7b-instruct-q4_K_M",
  "output_dir": "./output_docx",
  "last_mode": 1,
  "language": "en"
}
```

All fields are editable in the GUI's Dependencies / Output sections and are saved automatically on exit.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ffmpeg not found` | `brew install ffmpeg` or set `ffmpeg_path` in config |
| Setup wizard shows "openai-whisper" warning | Install whisper.cpp: `brew install whisper-cpp` |
| `whisper-cli` binary not found | Set path to `/usr/local/bin/whisper-cli` in GUI or config |
| Model file not found | Re-run wizard or set `whisper_model_path` in config |
| Output is Simplified Chinese | Update to latest version — OpenCC conversion is applied automatically |
| Ollama errors | `ollama serve` then `ollama pull qwen2.5:7b-instruct-q4_K_M` |
| Chinese misidentified as Japanese | Fixed in latest version — `-l zh` flag is always passed |

---

## Running Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

55 tests covering pipeline logic, GUI widgets, setup wizard, and the model downloader.

---

## License

MIT
