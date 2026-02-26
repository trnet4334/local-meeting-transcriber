"""Background QThread worker that runs the transcription pipeline."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, Signal

from localmeetingtranscriber.pipeline import PipelineInput, run_pipeline


class PipelineWorker(QThread):
    """Runs pipeline.run_pipeline() for a list of inputs on a background thread.

    All signals are automatically marshalled to the main thread's event loop
    by Qt's signal/slot mechanism, so UI updates are safe.
    """

    # Emitted for each log message (timestamped string)
    log_message: Signal = Signal(str)
    # Emitted when a file starts: (file_index, filename)
    file_started: Signal = Signal(int, str)
    # Emitted when a file finishes: (file_index, output_path)
    file_completed: Signal = Signal(int, Path)
    # Emitted with the current pipeline step description
    progress_updated: Signal = Signal(str)
    # Emitted once when all files have been processed successfully
    pipeline_finished: Signal = Signal()
    # Emitted on an unhandled exception with the error message
    error_occurred: Signal = Signal(str)

    def __init__(self, inputs: list[PipelineInput], parent=None) -> None:
        super().__init__(parent)
        self._inputs = inputs
        self._cancelled = False

    def cancel(self) -> None:
        """Request cancellation. The worker stops after the current file."""
        self._cancelled = True

    def run(self) -> None:
        """Execute the pipeline for each input. Called on the background thread."""
        for i, inp in enumerate(self._inputs):
            if self._cancelled:
                break

            self.file_started.emit(i, inp.file_path.name)

            def _on_progress(msg: str, _i: int = i) -> None:
                if not self._cancelled:
                    self.log_message.emit(msg)
                    self.progress_updated.emit(msg)

            try:
                output_path = run_pipeline(inp, on_progress=_on_progress)
            except Exception as exc:  # pylint: disable=broad-except
                self.error_occurred.emit(str(exc))
                return

            self.file_completed.emit(i, output_path)

        if not self._cancelled:
            self.pipeline_finished.emit()
