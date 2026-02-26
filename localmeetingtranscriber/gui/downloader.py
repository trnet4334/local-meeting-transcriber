"""Background thread for streaming file downloads with progress reporting."""
from __future__ import annotations

import urllib.request
from pathlib import Path

from PySide6.QtCore import QThread, Signal

_CHUNK_SIZE = 65_536  # 64 KB per read


class ModelDownloader(QThread):
    """Download *url* to *dest* in a background thread.

    Signals
    -------
    progress(downloaded_bytes, total_bytes)
        Emitted after each chunk.  total_bytes is 0 when Content-Length is
        absent (indeterminate progress).
    finished(dest_path)
        Emitted on successful completion.
    error(message)
        Emitted when an exception occurs or the download is cancelled with
        a partial file on disk.
    """

    progress = Signal(int, int)
    finished = Signal(Path)
    error = Signal(str)

    def __init__(self, url: str, dest: Path, parent=None) -> None:
        super().__init__(parent)
        self._url = url
        self._dest = dest
        self._cancelled = False

    def cancel(self) -> None:
        """Signal the download loop to stop on the next chunk boundary."""
        self._cancelled = True

    def run(self) -> None:  # noqa: C901
        try:
            req = urllib.request.Request(
                self._url,
                headers={"User-Agent": "LocalMeetingTranscriber/1.0"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0

                self._dest.parent.mkdir(parents=True, exist_ok=True)
                with open(self._dest, "wb") as fh:
                    while not self._cancelled:
                        chunk = resp.read(_CHUNK_SIZE)
                        if not chunk:
                            break
                        fh.write(chunk)
                        downloaded += len(chunk)
                        self.progress.emit(downloaded, total)

            if self._cancelled:
                # Remove incomplete file
                self._dest.unlink(missing_ok=True)
            else:
                self.finished.emit(self._dest)

        except Exception as exc:  # pylint: disable=broad-except
            self._dest.unlink(missing_ok=True)
            if not self._cancelled:
                self.error.emit(str(exc))
