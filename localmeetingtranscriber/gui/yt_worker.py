"""QThread worker for downloading audio from a URL via yt-dlp."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, Signal

from localmeetingtranscriber.youtube import download_url_audio


class UrlDownloadWorker(QThread):
    """Download audio from a URL in a background thread.

    Signals
    -------
    progress(float)
        Download progress in [0, 1].
    finished(Path, str)
        Emitted on success with the saved audio path and the video title.
    error(str)
        Emitted when an exception occurs.
    """

    progress = Signal(float)
    finished = Signal(Path, str)
    error = Signal(str)

    def __init__(self, url: str, dest_dir: Path, parent=None) -> None:
        super().__init__(parent)
        self._url = url
        self._dest_dir = dest_dir

    def run(self) -> None:
        try:
            audio_path, title = download_url_audio(
                self._url,
                self._dest_dir,
                on_progress=lambda pct: self.progress.emit(pct),
            )
            self.finished.emit(audio_path, title)
        except Exception as exc:  # pylint: disable=broad-except
            self.error.emit(str(exc))
