"""CLI entrypoint for LocalMeetingTranscriber."""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from localmeetingtranscriber.config import load_config, merge_overrides
from localmeetingtranscriber.converter import convert_to_wav
from localmeetingtranscriber.exporter import build_output_path, export_docx
from localmeetingtranscriber.llm_polisher import polish_text
from localmeetingtranscriber.postprocess import srt_to_lines, strip_timestamps
from localmeetingtranscriber.transcriber import transcribe_to_srt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = PROJECT_ROOT / "input_audio"
OUTPUT_DIR = PROJECT_ROOT / "output_docx"


def parse_selection(raw: str, max_count: int) -> list[int]:
    """Parse comma-separated 1-based indices into zero-based list."""
    indices: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        num = int(part)
        if num < 1 or num > max_count:
            raise ValueError("Selection out of range")
        indices.append(num - 1)
    return sorted(set(indices))


def mode_requires_ollama(mode: int) -> bool:
    """Return True if the selected mode requires Ollama."""
    return mode in (3, 4)


def list_m4a_files(input_dir: Path) -> list[Path]:
    """List .m4a files in the input directory."""
    if not input_dir.exists():
        return []
    return sorted(input_dir.glob("*.m4a"))


def prompt_mode() -> int:
    """Prompt user to select an output mode."""
    print("\nSelect output mode:")
    print("1. Full transcript with timestamps")
    print("2. Clean transcript without timestamps")
    print("3. Polished transcript (Ollama)")
    print("4. Polished transcript + appendix (raw transcript)")
    while True:
        raw = input("Enter choice (1-4): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= 4:
            return int(raw)
        print("Invalid choice. Please enter 1, 2, 3, or 4.")


def prompt_title_date(file_path: Path) -> tuple[str, str]:
    """Prompt for meeting title and date with defaults."""
    default_title = file_path.stem
    default_date = datetime.fromtimestamp(file_path.stat().st_mtime).strftime(
        "%Y-%m-%d"
    )
    title = input(f"Meeting title [{default_title}]: ").strip() or default_title
    date = input(f"Meeting date [{default_date}]: ").strip() or default_date
    return title, date


def check_command_exists(cmd: str) -> bool:
    """Check if a command exists on PATH."""
    return shutil.which(cmd) is not None


def resolve_file_path(path_str: str) -> Path:
    """Resolve a file path, treating relative paths as project-root relative."""
    path = Path(path_str).expanduser()
    if not path.is_absolute():
        path = (PROJECT_ROOT / path).resolve()
    return path


def resolve_optional_exe(path_str: str) -> str:
    """Resolve an executable path if it looks like a file path."""
    path = Path(path_str)
    if path.name != path_str:
        return str(resolve_file_path(path_str))
    return path_str


def validate_dependencies(config: dict, mode: int) -> None:
    """Validate required dependencies and raise RuntimeError if missing."""
    ffmpeg_path = config["ffmpeg_path"]
    whisper_cpp_path = resolve_file_path(config["whisper_cpp_path"])
    whisper_model_path = resolve_file_path(config["whisper_model_path"])

    if Path(ffmpeg_path).name == ffmpeg_path and not check_command_exists(ffmpeg_path):
        raise RuntimeError("ffmpeg not found. Install ffmpeg or update config.")

    if not whisper_cpp_path.exists():
        raise RuntimeError("whisper.cpp binary not found. Update config path.")

    if not whisper_model_path.exists():
        raise RuntimeError("whisper.cpp model not found. Update config path.")

    if mode_requires_ollama(mode):
        if not check_command_exists("ollama"):
            raise RuntimeError("Ollama not found. Install Ollama for polishing.")


def read_srt(srt_path: Path) -> str:
    """Read SRT file content."""
    return srt_path.read_text(encoding="utf-8")


def polish_with_ollama(model: str, text: str) -> str:
    """Polish text with a local LLM."""
    prompt = (
        "You are a professional meeting assistant. "
        "Polish the transcript for clarity, remove filler words, "
        "fix punctuation, and keep meaning. Preserve Chinese text.\n\n"
        f"Transcript:\n{text}\n"
    )
    return polish_text(model, prompt)


def process_file(file_path: Path, config: dict, mode: int) -> None:
    """Process a single audio file through the pipeline."""
    print(f"\nProcessing: {file_path.name}")
    title, date = prompt_title_date(file_path)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        wav_path = tmp_path / f"{file_path.stem}.wav"
        output_base = tmp_path / file_path.stem

        print("- Converting to WAV...")
        convert_to_wav(resolve_optional_exe(config["ffmpeg_path"]), file_path, wav_path)

        print("- Transcribing with whisper.cpp...")
        srt_path = transcribe_to_srt(
            str(resolve_file_path(config["whisper_cpp_path"])),
            resolve_file_path(config["whisper_model_path"]),
            wav_path,
            output_base,
        )

        print("- Post-processing transcript...")
        srt_text = read_srt(srt_path)
        raw_lines = srt_to_lines(srt_text)
        raw_txt_path = tmp_path / f"{file_path.stem}.txt"
        raw_txt_path.write_text("\n".join(raw_lines), encoding="utf-8")
        clean_lines = strip_timestamps(raw_lines)

        if mode == 1:
            final_lines = raw_lines
            appendix = None
        elif mode == 2:
            final_lines = clean_lines
            appendix = None
        elif mode == 3:
            print("- Polishing transcript with Ollama...")
            polished = polish_with_ollama(
                config["ollama_model"], "\n".join(clean_lines)
            )
            final_lines = polished.splitlines()
            appendix = None
        else:
            print("- Polishing transcript with Ollama...")
            polished = polish_with_ollama(
                config["ollama_model"], "\n".join(clean_lines)
            )
            final_lines = polished.splitlines()
            appendix = raw_lines

        output_path = build_output_path(OUTPUT_DIR, title)
        print(f"- Exporting DOCX to {output_path}...")
        export_docx(output_path, title, date, final_lines, appendix=appendix)

    print("- Done.")


def select_files(files: list[Path]) -> list[Path]:
    """Prompt user to select files by index."""
    if not files:
        return []

    print("\nAvailable .m4a files:")
    for i, path in enumerate(files, start=1):
        print(f"{i}. {path.name}")

    while True:
        raw = input("Select files (comma-separated indices): ").strip()
        try:
            indices = parse_selection(raw, len(files))
            return [files[i] for i in indices]
        except (ValueError, IndexError):
            print("Invalid selection. Try again.")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="LocalMeetingTranscriber")
    parser.add_argument(
        "--config",
        default=str(PROJECT_ROOT / "config.json"),
        help="Path to config.json",
    )
    parser.add_argument("--ffmpeg-path", default=None)
    parser.add_argument("--whisper-cpp-path", default=None)
    parser.add_argument("--whisper-model-path", default=None)
    parser.add_argument("--ollama-model", default=None)
    return parser.parse_args()


def main() -> int:
    """Run the interactive CLI."""
    args = parse_args()
    config = load_config(Path(args.config))
    overrides = {
        "ffmpeg_path": args.ffmpeg_path,
        "whisper_cpp_path": args.whisper_cpp_path,
        "whisper_model_path": args.whisper_model_path,
        "ollama_model": args.ollama_model,
    }
    config = merge_overrides(config, overrides)

    files = list_m4a_files(INPUT_DIR)
    if not files:
        print("No .m4a files found in input_audio/. Add files and retry.")
        return 1

    selected = select_files(files)
    if not selected:
        print("No files selected. Exiting.")
        return 1

    mode = prompt_mode()
    try:
        validate_dependencies(config, mode)
    except RuntimeError as exc:
        print(f"Dependency error: {exc}")
        return 1

    for file_path in selected:
        try:
            process_file(file_path, config, mode)
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Error processing {file_path.name}: {exc}")
            return 1

    print("\nAll done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
