"""CLI entrypoint for LocalMeetingTranscriber."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from localmeetingtranscriber.config import load_config, merge_overrides
from localmeetingtranscriber.pipeline import (
    PROJECT_ROOT,
    PipelineInput,
    validate_dependencies,
    run_pipeline,
)

INPUT_DIR = PROJECT_ROOT / "input_audio"
OUTPUT_DIR = PROJECT_ROOT / "output_docx"


def parse_selection(raw: str, max_count: int) -> list[int]:
    """Parse comma-separated 1-based indices into a sorted zero-based list."""
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
    """Prompt for meeting title and date with sensible defaults."""
    default_title = file_path.stem
    default_date = datetime.fromtimestamp(file_path.stat().st_mtime).strftime(
        "%Y-%m-%d"
    )
    title = input(f"Meeting title [{default_title}]: ").strip() or default_title
    date = input(f"Meeting date [{default_date}]: ").strip() or default_date
    return title, date


def process_file(file_path: Path, config: dict, mode: int) -> None:
    """Prompt for metadata then run the pipeline for a single audio file."""
    print(f"\nProcessing: {file_path.name}")
    title, date = prompt_title_date(file_path)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pipeline_input = PipelineInput(
        file_path=file_path,
        title=title,
        date=date,
        mode=mode,
        config=config,
        output_dir=OUTPUT_DIR,
    )
    run_pipeline(pipeline_input, on_progress=lambda msg: print(f"- {msg}"))


def select_files(files: list[Path]) -> list[Path]:
    """Prompt user to select files from the list by index."""
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
