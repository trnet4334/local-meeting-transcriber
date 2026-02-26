# LocalMeetingTranscriber - Codex Agent Specification

## Overview
This AGENT defines the tasks for generating a Python CLI application called **LocalMeetingTranscriber**. 
The application processes iPhone .m4a audio recordings into meeting transcripts and exports them as Word (.docx) files.

---

## Project Requirements

1. **Input & Conversion**
   - Read all `.m4a` files from `input_audio/`.
   - Convert each file to 16kHz mono `.wav` using `ffmpeg`.

2. **Transcription**
   - Run `whisper.cpp` with the `large-v3 Q5_0` model.
   - Generate raw transcripts with optional timestamps.

3. **CLI Menu**
   - Prompt user to choose one of four modes:
     1. Full transcript with timestamps
     2. Clean transcript without timestamps
     3. Polished transcript (using local LLM via Ollama)
     4. Polished transcript with appendix including raw transcript
   - Provide clear progress and error messages.
   - Validate inputs and handle missing dependencies gracefully.

4. **Post-processing**
   - Optionally remove timestamps.
   - If polishing is selected, call local Ollama with `qwen2.5:7b-instruct-q4_K_M`.
   - Prepare final transcript for Word output.

5. **Word Output**
   - Use `python-docx`.
   - Include title, date, transcript content.
   - Mode 4: include appendix with raw transcript.
   - Save into `output_docx/` folder.
   - File naming: `YYYY-MM-DD_<meeting-name>_<mode>.docx`.

6. **Project Structure**
   - `main.py` orchestrates the workflow.
   - `core/` modules:
     - `converter.py` (ffmpeg conversion)
     - `transcriber.py` (whisper.cpp invocation)
     - `postprocess.py` (cleaning and timestamp removal)
     - `exporter.py` (docx generation)
     - `llm_polisher.py` (optional LLM-based polish)
   - `config/settings.yaml` for adjustable parameters.
   - `README.md` with installation, usage, examples, and folder structure.

7. **Code Quality**
   - Use functions/modules; avoid huge scripts.
   - Include docstrings and inline comments in English.
   - Python 3.11 compatible.
   - Include `requirements.txt`.

---

## CLI Behavior
- List all `.m4a` files.
- Prompt user to choose mode (1–4).
- Execute conversion, transcription, postprocessing, and docx export.
- Show progress and handle errors.
- Each file is processed individually or in batch.

---

## Documentation Requirements
- Generate a comprehensive `README.md` including:
  - Project description
  - Installation instructions (including ffmpeg & whisper.cpp setup)
  - CLI usage examples
  - Example command flow for each mode
  - Expected folder structure
  - Sample output snippet
  - Tips for users

---

## Output
- Full project structure and code.
- All files complete and runnable.
- Example docx output for reference included in README.

---

## Quality Constraints
- All code modular and well-documented.
- UTF-8 safe and handles Traditional Chinese.
- Graceful error handling.
- No cloud dependencies except optional local LLM.

---

## Usage Example (for Codex)