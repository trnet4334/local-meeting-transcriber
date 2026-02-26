"""URL-based audio extraction for LocalMeetingTranscriber.

Supports any URL that yt-dlp handles — YouTube, Vimeo, Bilibili, direct
video file URLs (.mp4, .mov, …), and 1000+ other platforms.

Public API
----------
is_url(text)              → True if the string looks like an http(s) URL
download_url_audio(url, dest_dir, on_progress) → (Path, title)
"""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

# ---------------------------------------------------------------------------
# URL detection helpers
# ---------------------------------------------------------------------------

_MEDIA_EXTENSIONS = {
    ".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v",
    ".flv", ".ts", ".wmv", ".ogv",
}


def is_url(text: str) -> bool:
    """Return True if *text* looks like an HTTP(S) URL."""
    return text.startswith(("http://", "https://"))


def is_direct_media_url(url: str) -> bool:
    """Return True if the URL points directly to a video/audio file."""
    path_part = url.split("?")[0].split("#")[0]
    return Path(path_part).suffix.lower() in _MEDIA_EXTENSIONS


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

ProgressCallback = Callable[[float], None]  # 0.0 – 1.0


def download_url_audio(
    url: str,
    dest_dir: Path,
    on_progress: ProgressCallback | None = None,
) -> tuple[Path, str]:
    """Download audio from *url* and save as .m4a in *dest_dir*.

    Parameters
    ----------
    url:
        Any URL supported by yt-dlp (YouTube, Vimeo, direct .mp4, …).
    dest_dir:
        Directory where the audio file will be saved.
    on_progress:
        Optional callback receiving a float in [0, 1] as download progresses.

    Returns
    -------
    (audio_path, title)
        ``audio_path`` is the saved .m4a file; ``title`` is the video title
        extracted from metadata (empty string if unavailable).

    Raises
    ------
    ImportError
        If yt-dlp is not installed.
    yt_dlp.utils.DownloadError
        If the URL cannot be downloaded.
    """
    try:
        import yt_dlp
    except ImportError as exc:
        raise ImportError(
            "yt-dlp is required for URL downloads. "
            "Install it with: pip install yt-dlp"
        ) from exc

    dest_dir.mkdir(parents=True, exist_ok=True)
    result: dict = {}

    def _hook(d: dict) -> None:
        status = d.get("status")
        if status == "downloading" and on_progress:
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            if total > 0:
                on_progress(min(downloaded / total, 1.0))
        elif status == "finished":
            result["path"] = Path(d["filename"])

    ydl_opts: dict = {
        "format": "bestaudio/best",
        "outtmpl": str(dest_dir / "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }
        ],
        "progress_hooks": [_hook],
        # Suppress console output
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title: str = info.get("title", "") if info else ""

    # After postprocessing the extension changes to .m4a
    raw_path = result.get("path", dest_dir / f"{title}.m4a")
    audio_path = Path(str(raw_path).rsplit(".", 1)[0] + ".m4a")

    if not audio_path.exists():
        # Fallback: find the newest .m4a in dest_dir
        candidates = sorted(dest_dir.glob("*.m4a"), key=lambda p: p.stat().st_mtime)
        if candidates:
            audio_path = candidates[-1]

    return audio_path, title
