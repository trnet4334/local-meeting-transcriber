"""Main application window for LocalMeetingTranscriber."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from localmeetingtranscriber.config import load_config, save_config
from localmeetingtranscriber.pipeline import (
    PROJECT_ROOT,
    PipelineInput,
    validate_dependencies,
)
from localmeetingtranscriber.gui.worker import PipelineWorker

_CONFIG_PATH = PROJECT_ROOT / "config.json"

_MODES = [
    "1. Full transcript with timestamps",
    "2. Clean transcript without timestamps",
    "3. Polished transcript (Ollama)",
    "4. Polished transcript + raw appendix (Ollama)",
]


class MainWindow(QMainWindow):
    """Single-window GUI for the LocalMeetingTranscriber application."""

    def __init__(self) -> None:
        super().__init__()
        self._config = load_config(_CONFIG_PATH)
        self._worker: PipelineWorker | None = None

        self.setWindowTitle("LocalMeetingTranscriber")
        self.setMinimumSize(760, 700)
        self._build_ui()
        self._connect_signals()
        self._update_start_button()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        layout.addWidget(self._build_file_group())
        layout.addWidget(self._build_settings_group())
        layout.addWidget(self._build_metadata_group())
        layout.addLayout(self._build_action_bar())
        layout.addWidget(self._build_progress_group())
        layout.addWidget(self._build_log_group(), stretch=1)

    def _build_file_group(self) -> QGroupBox:
        group = QGroupBox("Input Files")
        layout = QVBoxLayout(group)

        self._file_list = QListWidget()
        self._file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        layout.addWidget(self._file_list)

        btn_row = QHBoxLayout()
        self._btn_add = QPushButton("Add Files…")
        self._btn_remove = QPushButton("Remove Selected")
        btn_row.addWidget(self._btn_add)
        btn_row.addWidget(self._btn_remove)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        return group

    def _build_settings_group(self) -> QGroupBox:
        group = QGroupBox("Settings")
        form = QFormLayout(group)

        self._mode_combo = QComboBox()
        for label in _MODES:
            self._mode_combo.addItem(label)
        last_mode = int(self._config.get("last_mode", 1))
        self._mode_combo.setCurrentIndex(max(0, last_mode - 1))
        form.addRow("Output Mode:", self._mode_combo)

        folder_row = QHBoxLayout()
        default_out = str(
            (PROJECT_ROOT / self._config.get("output_dir", "output_docx")).resolve()
        )
        self._output_dir_edit = QLineEdit(default_out)
        self._btn_browse = QPushButton("Browse…")
        folder_row.addWidget(self._output_dir_edit, stretch=1)
        folder_row.addWidget(self._btn_browse)
        form.addRow("Output Folder:", folder_row)
        return group

    def _build_metadata_group(self) -> QGroupBox:
        group = QGroupBox("Meeting Metadata (editable)")
        layout = QVBoxLayout(group)

        self._metadata_table = QTableWidget(0, 3)
        self._metadata_table.setHorizontalHeaderLabels(["File", "Title", "Date"])
        self._metadata_table.horizontalHeader().setStretchLastSection(False)
        self._metadata_table.setColumnWidth(0, 200)
        self._metadata_table.setColumnWidth(1, 280)
        self._metadata_table.setColumnWidth(2, 110)
        self._metadata_table.setMaximumHeight(160)
        layout.addWidget(self._metadata_table)
        return group

    def _build_action_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        self._btn_start = QPushButton("Start Processing")
        self._btn_start.setDefault(True)
        self._btn_cancel = QPushButton("Cancel")
        self._btn_cancel.setEnabled(False)
        bar.addStretch()
        bar.addWidget(self._btn_start)
        bar.addWidget(self._btn_cancel)
        return bar

    def _build_progress_group(self) -> QGroupBox:
        group = QGroupBox("Progress")
        layout = QVBoxLayout(group)

        layout.addWidget(QLabel("Overall:"))
        self._progress_overall = QProgressBar()
        self._progress_overall.setValue(0)
        layout.addWidget(self._progress_overall)

        self._step_label = QLabel("Current step:")
        layout.addWidget(self._step_label)
        self._progress_step = QProgressBar()
        self._progress_step.setRange(0, 100)
        self._progress_step.setValue(0)
        layout.addWidget(self._progress_step)
        return group

    def _build_log_group(self) -> QGroupBox:
        group = QGroupBox("Log")
        layout = QVBoxLayout(group)
        self._log_area = QTextEdit()
        self._log_area.setReadOnly(True)
        self._log_area.setFontFamily("Menlo, Monaco, monospace")
        layout.addWidget(self._log_area)
        return group

    # ------------------------------------------------------------------
    # Signal connections
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        self._btn_add.clicked.connect(self._on_add_files_clicked)
        self._btn_remove.clicked.connect(self._on_remove_selected)
        self._btn_browse.clicked.connect(self._on_browse_output)
        self._btn_start.clicked.connect(self._on_start)
        self._btn_cancel.clicked.connect(self._on_cancel)

    # ------------------------------------------------------------------
    # File management
    # ------------------------------------------------------------------

    def _on_add_files_clicked(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select .m4a Audio Files",
            str(Path.home()),
            "Audio Files (*.m4a)",
        )
        if paths:
            self._add_files(paths)

    def _add_files(self, paths: list[str]) -> None:
        """Add files to the list and metadata table (skips duplicates)."""
        existing = {
            self._file_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self._file_list.count())
        }
        for path_str in paths:
            if path_str in existing:
                continue
            path = Path(path_str)
            item = QListWidgetItem(path.name)
            item.setData(Qt.ItemDataRole.UserRole, path_str)
            self._file_list.addItem(item)

            row = self._metadata_table.rowCount()
            self._metadata_table.insertRow(row)
            name_item = QTableWidgetItem(path.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._metadata_table.setItem(row, 0, name_item)
            self._metadata_table.setItem(row, 1, QTableWidgetItem(path.stem))
            try:
                mdate = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")
            except OSError:
                mdate = datetime.today().strftime("%Y-%m-%d")
            self._metadata_table.setItem(row, 2, QTableWidgetItem(mdate))

        self._update_start_button()

    def _on_remove_selected(self) -> None:
        rows = sorted(
            {self._file_list.row(item) for item in self._file_list.selectedItems()},
            reverse=True,
        )
        for row in rows:
            self._file_list.takeItem(row)
            self._metadata_table.removeRow(row)
        self._update_start_button()

    def _on_browse_output(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Folder", self._output_dir_edit.text()
        )
        if directory:
            self._output_dir_edit.setText(directory)

    def _update_start_button(self) -> None:
        self._btn_start.setEnabled(self._file_list.count() > 0)

    # ------------------------------------------------------------------
    # Pipeline start / cancel
    # ------------------------------------------------------------------

    def _on_start(self) -> None:
        mode = self._mode_combo.currentIndex() + 1
        output_dir = Path(self._output_dir_edit.text())

        try:
            validate_dependencies(self._config, mode)
        except RuntimeError as exc:
            QMessageBox.critical(self, "Dependency Error", str(exc))
            return

        inputs: list[PipelineInput] = []
        for i in range(self._file_list.count()):
            path_str = self._file_list.item(i).data(Qt.ItemDataRole.UserRole)
            file_path = Path(path_str)
            title = (self._metadata_table.item(i, 1) or QTableWidgetItem(file_path.stem)).text().strip() or file_path.stem
            date = (self._metadata_table.item(i, 2) or QTableWidgetItem("")).text().strip()
            inputs.append(
                PipelineInput(
                    file_path=file_path,
                    title=title,
                    date=date,
                    mode=mode,
                    config=self._config,
                    output_dir=output_dir,
                )
            )

        self._worker = PipelineWorker(inputs)
        self._worker.log_message.connect(self._on_log_message)
        self._worker.file_started.connect(self._on_file_started)
        self._worker.file_completed.connect(self._on_file_completed)
        self._worker.progress_updated.connect(self._on_progress_updated)
        self._worker.pipeline_finished.connect(self._on_pipeline_finished)
        self._worker.error_occurred.connect(self._on_error_occurred)

        self._btn_start.setEnabled(False)
        self._btn_cancel.setEnabled(True)
        self._progress_overall.setRange(0, len(inputs))
        self._progress_overall.setValue(0)
        self._progress_step.setRange(0, 0)  # indeterminate / pulsing
        self._log_area.clear()

        self._worker.start()

    def _on_cancel(self) -> None:
        if self._worker:
            self._worker.cancel()
        self._btn_cancel.setEnabled(False)
        self._log_area.append("— Cancellation requested —")

    # ------------------------------------------------------------------
    # Worker signal handlers
    # ------------------------------------------------------------------

    def _on_file_started(self, index: int, name: str) -> None:
        total = self._progress_overall.maximum()
        self._progress_overall.setValue(index)
        self._log_area.append(f"\n[{index + 1}/{total}] Processing: {name}")

    def _on_progress_updated(self, msg: str) -> None:
        self._step_label.setText(f"Current step: {msg}")

    def _on_log_message(self, msg: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_area.append(f"[{ts}] {msg}")

    def _on_file_completed(self, index: int, output_path: Path) -> None:
        self._progress_overall.setValue(index + 1)
        self._log_area.append(f"✓ Saved: {output_path}")

    def _on_pipeline_finished(self) -> None:
        self._progress_step.setRange(0, 100)
        self._progress_step.setValue(100)
        self._step_label.setText("Current step: Done")
        self._btn_start.setEnabled(True)
        self._btn_cancel.setEnabled(False)
        self._log_area.append("\n✓ All files processed successfully.")
        QMessageBox.information(self, "Done", "All files processed successfully.")
        self._try_notify("All files processed successfully.")

    def _on_error_occurred(self, message: str) -> None:
        self._progress_step.setRange(0, 100)
        self._progress_step.setValue(0)
        self._step_label.setText("Current step: Error")
        self._btn_start.setEnabled(True)
        self._btn_cancel.setEnabled(False)
        self._log_area.append(f"\n✗ Error: {message}")
        QMessageBox.critical(self, "Pipeline Error", message)

    # ------------------------------------------------------------------
    # macOS notification
    # ------------------------------------------------------------------

    def _try_notify(self, message: str) -> None:
        """Best-effort macOS notification; silently ignored if unavailable."""
        try:
            from PySide6.QtWidgets import QSystemTrayIcon
            if QSystemTrayIcon.isSystemTrayAvailable():
                tray = QSystemTrayIcon(self)
                tray.show()
                tray.showMessage("LocalMeetingTranscriber", message)
        except Exception:  # pylint: disable=broad-except
            pass

    # ------------------------------------------------------------------
    # Config persistence on close
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait(3000)

        updated = {
            **self._config,
            "last_mode": self._mode_combo.currentIndex() + 1,
            "output_dir": self._output_dir_edit.text(),
        }
        try:
            save_config(_CONFIG_PATH, updated)
        except OSError:
            pass
        super().closeEvent(event)
