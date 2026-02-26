# LocalMeetingTranscriber

LocalMeetingTranscriber is an interactive CLI that turns iPhone `.m4a` recordings into Word `.docx` meeting transcripts. It converts audio to 16kHz mono WAV via `ffmpeg`, transcribes with `whisper.cpp` (large-v3 Q5_0), optionally polishes text with a local Ollama model, and exports clean Word documents.

## Features
- Interactive multi-select of `.m4a` files in `input_audio/`
- Four output modes:
  1. Full transcript with timestamps
  2. Clean transcript without timestamps
  3. Polished transcript (Ollama)
  4. Polished transcript with appendix (raw transcript)
- Exports `.docx` files to `output_docx/`
- UTF-8 and Chinese text support

## Requirements
- Python 3.11
- `ffmpeg`
- `whisper.cpp` built locally
- `ollama` (only required for modes 3 and 4)

Python dependencies:
- `python-docx`
- `pytest` (for tests)

Install Python deps:

```bash
pip install -r requirements.txt
```

## Setup: ffmpeg
Install ffmpeg using your preferred method.

Examples:

```bash
# macOS (Homebrew)
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg
```

## Setup: whisper.cpp
1. Clone and build whisper.cpp:

```bash
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp
make
```

2. Download the large-v3 Q5_0 model:

```bash
# Example from whisper.cpp model tooling
# (Choose a trusted mirror or the official whisper.cpp model scripts)
```

3. Update `config.json` or use CLI flags to point to:
- `whisper_cpp_path`: `./whisper.cpp/main` (or absolute path)
- `whisper_model_path`: `./models/ggml-large-v3-q5_0.bin`

## Setup: Ollama (Optional)
Modes 3 and 4 require Ollama and the model `qwen2.5:7b-instruct-q4_K_M`.

```bash
ollama pull qwen2.5:7b-instruct-q4_K_M
```

## Folder Structure

```
LocalMeetingTranscriber/
  localmeetingtranscriber/
  input_audio/           # Put .m4a files here
  output_docx/           # Generated .docx files
  config.json
  requirements.txt
  README.md
```

## CLI Usage

Run the CLI:

```bash
python -m localmeetingtranscriber.main
```

Install as a CLI and run via `lmt`:

```bash
pip install -e .
lmt
```

Optional overrides:

```bash
python -m localmeetingtranscriber.main \
  --config ./config.json \
  --ffmpeg-path /usr/local/bin/ffmpeg \
  --whisper-cpp-path /path/to/whisper.cpp/main \
  --whisper-model-path /path/to/ggml-large-v3-q5_0.bin \
  --ollama-model qwen2.5:7b-instruct-q4_K_M
```

## Example Flows

### Mode 1: Full transcript with timestamps
```
$ python -m localmeetingtranscriber.main
Available .m4a files:
1. team_sync.m4a
2. customer_call.m4a
Select files (comma-separated indices): 1

Select output mode:
1. Full transcript with timestamps
2. Clean transcript without timestamps
3. Polished transcript (Ollama)
4. Polished transcript + appendix (raw transcript)
Enter choice (1-4): 1
Meeting title [team_sync]: Weekly Team Sync
Meeting date [2026-02-24]: 2026-02-25
- Converting to WAV...
- Transcribing with whisper.cpp...
- Post-processing transcript...
- Exporting DOCX to output_docx/Weekly Team Sync.docx...
- Done.
```

### Mode 2: Clean transcript
```
Select files (comma-separated indices): 1,2
Enter choice (1-4): 2
Meeting title [team_sync]:
Meeting date [2026-02-24]:
...
```

### Mode 3: Polished transcript (Ollama)
```
Select files (comma-separated indices): 2
Enter choice (1-4): 3
- Polishing transcript with Ollama...
```

### Mode 4: Polished + appendix
```
Select files (comma-separated indices): 1
Enter choice (1-4): 4
- Polishing transcript with Ollama...
- Exporting DOCX to output_docx/Weekly Team Sync.docx...
```

## Sample Output Snippet (DOCX Content)

```
Weekly Team Sync
Date: 2026-02-25

[00:00:03] Today we will review the project status and next steps.
[00:00:12] The frontend is complete; backend integration is in progress.

Appendix: Raw Transcript
[00:00:03] Today we will review the project status and next steps.
[00:00:12] The frontend is complete; backend integration is in progress.
```

## Tips
- Use short filenames; they become default meeting titles.
- Keep a consistent naming format to organize outputs.
- If Ollama isn’t installed, use mode 1 or 2.
- For best results, record in quiet environments.

## Troubleshooting
- **ffmpeg not found**: Install ffmpeg or set `ffmpeg_path` in `config.json`.
- **whisper.cpp not found**: Build whisper.cpp and update `whisper_cpp_path`.
- **model not found**: Download `ggml-large-v3-q5_0.bin` and update `whisper_model_path`.
- **Ollama errors**: Install Ollama and pull `qwen2.5:7b-instruct-q4_K_M`.
