# LocalMeetingTranscriber Design (2026-02-25)

## Summary
Build a temporary, interactive CLI that converts iPhone `.m4a` recordings into `.docx` meeting transcripts using `ffmpeg`, `whisper.cpp`, and optional local LLM polishing via Ollama. The CLI supports multi-select input files, four output modes, editable meeting metadata, and cleans up intermediate artifacts.

## Goals
- Interactive CLI with multi-select of `.m4a` files from `input_audio/`.
- Convert audio to 16kHz mono `.wav` via `ffmpeg`.
- Run `whisper.cpp` with large-v3 Q5_0 model to generate SRT.
- Postprocess SRT to raw transcript and optional timestamp stripping.
- Optional polishing via Ollama using `qwen2.5:7b-instruct-q4_K_M` (hard error if missing).
- Export `.docx` with title, date, transcript, and optional appendix.
- Configurable paths via both CLI flags and `config.json`.
- Python 3.11 compatible, modular code.

## Non-Goals
- Non-interactive/batch-only operation.
- GUI implementation (only prepare for future GUI with config + module boundaries).
- Word-level timestamps.

## Approach Options Considered
1. **Minimal CLI + modular pipeline (Chosen)**
   - Fast to implement, clean module boundaries, GUI-friendly via config.
2. Config-first + non-interactive batch
   - More flexibility but more complexity than needed for a temporary CLI.
3. GUI-ready architecture with event hooks
   - Overkill for current scope.

## Architecture
Modules and responsibilities:
- `main.py`: CLI entry, file selection, mode selection, metadata prompts, pipeline orchestration.
- `config.py`: load `config.json`, merge CLI overrides, validate paths.
- `converter.py`: `.m4a` → `.wav` (16kHz, mono) using `ffmpeg`.
- `transcriber.py`: run `whisper.cpp` to produce `.srt`.
- `postprocess.py`: convert SRT to raw transcript; strip timestamps if needed.
- `llm_polisher.py`: call Ollama for text refinement (hard-fail if missing).
- `exporter.py`: create `.docx` via `python-docx` with UTF-8/Chinese support.

## Data Flow
1. List `.m4a` files in `input_audio/` and allow multi-select.
2. For each file:
   - Prompt for meeting title and date (editable).
   - Convert to `.wav` temp file.
   - Run `whisper.cpp` to generate `.srt`.
   - Convert `.srt` → raw transcript text.
   - If clean: strip timestamps.
   - If polished: send cleaned text to Ollama (hard-fail on errors).
   - Export `.docx` to `output_docx/` with title/date/body (+ appendix for mode 4).
   - Delete intermediate files (`.wav`, `.srt`, raw `.txt`).

## CLI Behavior
- Interactive-only; validates file selection and mode input.
- Prints progress and actionable error messages.
- Supports configuration via `config.json` and CLI overrides for paths.

## Error Handling
- Validate existence of `ffmpeg`, `whisper.cpp` binary, and model path.
- For modes 3/4: Ollama and model are required; missing dependencies are fatal.
- Other missing dependencies are reported with remediation guidance.

## Testing Strategy (Lightweight)
- Smoke test on a short `.m4a` to verify conversion, transcription, and export.
- Polishing mode test to confirm Ollama integration and failure behavior.

## Output Format
`.docx` structure:
- Title (meeting name)
- Date
- Transcript content
- Optional appendix with raw transcript + timestamps (mode 4)

## Folder Structure
```
input_audio/   # user-provided .m4a files
output_docx/   # generated .docx files
```

## Implementation Notes
- Use `--output-srt` from `whisper.cpp` and parse SRT to line-level timestamps.
- Use `python-docx` for Word generation; ensure UTF-8 content passes through.
- Clean intermediates after export.
