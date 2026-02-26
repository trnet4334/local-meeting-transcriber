"""Main application window for LocalMeetingTranscriber."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
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
    QScrollArea,
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
from localmeetingtranscriber.gui.i18n import DEFAULT_LANGUAGE, LANGUAGES, TRANSLATIONS

_CONFIG_PATH = PROJECT_ROOT / "config.json"


class MainWindow(QMainWindow):
    """Single-window GUI for the LocalMeetingTranscriber application."""

    def __init__(self) -> None:
        super().__init__()
        self._config = load_config(_CONFIG_PATH)
        self._worker: PipelineWorker | None = None
        self._lang = self._config.get("language", DEFAULT_LANGUAGE)
        if self._lang not in TRANSLATIONS:
            self._lang = DEFAULT_LANGUAGE

        self.setWindowTitle(self._tr("window_title"))
        self.setMinimumSize(820, 920)
        self._build_ui()
        self._connect_signals()
        self.setStyleSheet("QLineEdit { padding: 3px 6px; }")
        self._update_start_button()

    # ------------------------------------------------------------------
    # Internationalisation
    # ------------------------------------------------------------------

    def _tr(self, key: str) -> str:
        """Return the translated string for *key* in the active language."""
        return (
            TRANSLATIONS.get(self._lang, TRANSLATIONS[DEFAULT_LANGUAGE]).get(key)
            or TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key)
        )

    def _on_language_changed(self, index: int) -> None:
        codes = list(LANGUAGES.keys())
        self._lang = codes[index] if 0 <= index < len(codes) else DEFAULT_LANGUAGE
        self._retranslate_ui()

    def _retranslate_ui(self) -> None:
        """Update every UI string to the currently selected language."""
        self.setWindowTitle(self._tr("window_title"))
        self._lang_selector_label.setText(self._tr("lang_label"))

        # Group boxes
        self._grp_input.setTitle(self._tr("group_input"))
        self._grp_output.setTitle(self._tr("group_output"))
        self._grp_deps.setTitle(self._tr("group_deps"))
        self._grp_metadata.setTitle(self._tr("group_metadata"))
        self._grp_progress.setTitle(self._tr("group_progress"))
        self._grp_log.setTitle(self._tr("group_log"))

        # Buttons
        self._btn_add.setText(self._tr("btn_add"))
        self._btn_remove.setText(self._tr("btn_remove"))
        self._btn_browse.setText(self._tr("btn_browse"))
        self._btn_browse_whisper_bin.setText(self._tr("btn_browse"))
        self._btn_browse_whisper_model.setText(self._tr("btn_browse"))
        self._btn_start.setText(self._tr("btn_start"))
        self._btn_cancel.setText(self._tr("btn_cancel"))

        # Form labels
        self._lbl_mode.setText(self._tr("lbl_mode"))
        self._lbl_output_folder.setText(self._tr("lbl_output_folder"))
        self._lbl_ffmpeg.setText(self._tr("lbl_ffmpeg"))
        self._lbl_whisper_bin.setText(self._tr("lbl_whisper_bin"))
        self._lbl_whisper_model.setText(self._tr("lbl_whisper_model"))
        self._lbl_ollama_model.setText(self._tr("lbl_ollama_model"))
        self._lbl_overall.setText(self._tr("lbl_overall"))
        self._step_label.setText(self._tr("lbl_current_step"))

        # Mode combo items
        for i, key in enumerate(["mode_1", "mode_2", "mode_3", "mode_4"]):
            self._mode_combo.setItemText(i, self._tr(key))

        # Table headers
        self._metadata_table.setHorizontalHeaderLabels([
            self._tr("col_file"),
            self._tr("col_title"),
            self._tr("col_date"),
        ])

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)

        # ── Language selector bar ──────────────────────────────────────
        lang_bar_widget = QWidget()
        lang_bar = QHBoxLayout(lang_bar_widget)
        lang_bar.setContentsMargins(16, 6, 16, 6)
        self._lang_selector_label = QLabel(self._tr("lang_label"))
        self._lang_combo = QComboBox()
        for code, name in LANGUAGES.items():
            self._lang_combo.addItem(name, code)
        codes = list(LANGUAGES.keys())
        self._lang_combo.setCurrentIndex(codes.index(self._lang) if self._lang in codes else 0)
        lang_bar.addStretch()
        lang_bar.addWidget(self._lang_selector_label)
        lang_bar.addWidget(self._lang_combo)
        wrapper_layout.addWidget(lang_bar_widget)

        # ── Scrollable content ─────────────────────────────────────────
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(14)
        layout.setContentsMargins(16, 16, 16, 16)

        layout.addWidget(self._build_file_group())
        layout.addWidget(self._build_output_group())
        layout.addWidget(self._build_dependencies_group())
        layout.addWidget(self._build_metadata_group())
        layout.addLayout(self._build_action_bar())
        layout.addWidget(self._build_progress_group())
        layout.addWidget(self._build_log_group())
        layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        wrapper_layout.addWidget(scroll)

        self.setCentralWidget(wrapper)

    def _build_file_group(self) -> QGroupBox:
        self._grp_input = QGroupBox(self._tr("group_input"))
        layout = QVBoxLayout(self._grp_input)

        self._file_list = QListWidget()
        self._file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        layout.addWidget(self._file_list)

        btn_row = QHBoxLayout()
        self._btn_add = QPushButton(self._tr("btn_add"))
        self._btn_remove = QPushButton(self._tr("btn_remove"))
        btn_row.addWidget(self._btn_add)
        btn_row.addWidget(self._btn_remove)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        return self._grp_input

    @staticmethod
    def _make_form(group: QGroupBox) -> QVBoxLayout:
        """VBox-based form layout with guaranteed row spacing."""
        vbox = QVBoxLayout(group)
        vbox.setSpacing(0)
        vbox.setContentsMargins(14, 16, 14, 16)
        return vbox

    @staticmethod
    def _form_row(label: QLabel, field_widget) -> QWidget:
        """Wrap a label + field pair in a QWidget with 12 px top padding."""
        container = QWidget()
        container.setContentsMargins(0, 12, 0, 0)
        hbox = QHBoxLayout(container)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(12)
        label.setFixedWidth(155)
        hbox.addWidget(label)
        if isinstance(field_widget, QHBoxLayout):
            hbox.addLayout(field_widget, stretch=1)
        else:
            hbox.addWidget(field_widget, stretch=1)
        return container

    @staticmethod
    def _browse_row(edit: QLineEdit, btn: QPushButton) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(edit, stretch=1)
        row.addWidget(btn)
        return row

    def _build_output_group(self) -> QGroupBox:
        self._grp_output = QGroupBox(self._tr("group_output"))
        vbox = self._make_form(self._grp_output)

        self._lbl_mode = QLabel(self._tr("lbl_mode"))
        self._mode_combo = QComboBox()
        self._mode_combo.setFixedHeight(34)
        for key in ["mode_1", "mode_2", "mode_3", "mode_4"]:
            self._mode_combo.addItem(self._tr(key))
        last_mode = int(self._config.get("last_mode", 1))
        self._mode_combo.setCurrentIndex(max(0, last_mode - 1))
        vbox.addWidget(self._form_row(self._lbl_mode, self._mode_combo))

        self._lbl_output_folder = QLabel(self._tr("lbl_output_folder"))
        default_out = self._config.get("output_dir", "")
        if not default_out or not Path(default_out).is_absolute():
            default_out = str((PROJECT_ROOT / "output_docx").resolve())
        self._output_dir_edit = QLineEdit(default_out)
        self._output_dir_edit.setFixedHeight(34)
        self._btn_browse = QPushButton(self._tr("btn_browse"))
        self._btn_browse.setFixedHeight(34)
        vbox.addWidget(self._form_row(
            self._lbl_output_folder,
            self._browse_row(self._output_dir_edit, self._btn_browse),
        ))

        vbox.addStretch()
        return self._grp_output

    def _build_dependencies_group(self) -> QGroupBox:
        self._grp_deps = QGroupBox(self._tr("group_deps"))
        vbox = self._make_form(self._grp_deps)

        self._lbl_ffmpeg = QLabel(self._tr("lbl_ffmpeg"))
        self._ffmpeg_path_edit = QLineEdit(self._config.get("ffmpeg_path", "ffmpeg"))
        self._ffmpeg_path_edit.setFixedHeight(34)
        vbox.addWidget(self._form_row(self._lbl_ffmpeg, self._ffmpeg_path_edit))

        self._lbl_whisper_bin = QLabel(self._tr("lbl_whisper_bin"))
        self._whisper_bin_edit = QLineEdit(self._config.get("whisper_cpp_path", ""))
        self._whisper_bin_edit.setFixedHeight(34)
        self._whisper_bin_edit.setPlaceholderText("/path/to/whisper.cpp/main")
        self._btn_browse_whisper_bin = QPushButton(self._tr("btn_browse"))
        self._btn_browse_whisper_bin.setFixedHeight(34)
        vbox.addWidget(self._form_row(
            self._lbl_whisper_bin,
            self._browse_row(self._whisper_bin_edit, self._btn_browse_whisper_bin),
        ))

        self._lbl_whisper_model = QLabel(self._tr("lbl_whisper_model"))
        self._whisper_model_edit = QLineEdit(self._config.get("whisper_model_path", ""))
        self._whisper_model_edit.setFixedHeight(34)
        self._whisper_model_edit.setPlaceholderText("/path/to/ggml-large-v3-q5_0.bin")
        self._btn_browse_whisper_model = QPushButton(self._tr("btn_browse"))
        self._btn_browse_whisper_model.setFixedHeight(34)
        vbox.addWidget(self._form_row(
            self._lbl_whisper_model,
            self._browse_row(self._whisper_model_edit, self._btn_browse_whisper_model),
        ))

        self._lbl_ollama_model = QLabel(self._tr("lbl_ollama_model"))
        self._ollama_model_edit = QLineEdit(self._config.get("ollama_model", ""))
        self._ollama_model_edit.setFixedHeight(34)
        self._ollama_model_edit.setPlaceholderText("qwen2.5:7b-instruct-q4_K_M")
        vbox.addWidget(self._form_row(self._lbl_ollama_model, self._ollama_model_edit))

        return self._grp_deps

    def _build_metadata_group(self) -> QGroupBox:
        self._grp_metadata = QGroupBox(self._tr("group_metadata"))
        layout = QVBoxLayout(self._grp_metadata)

        self._metadata_table = QTableWidget(0, 3)
        self._metadata_table.setHorizontalHeaderLabels([
            self._tr("col_file"),
            self._tr("col_title"),
            self._tr("col_date"),
        ])
        self._metadata_table.horizontalHeader().setStretchLastSection(False)
        self._metadata_table.setColumnWidth(0, 200)
        self._metadata_table.setColumnWidth(1, 280)
        self._metadata_table.setColumnWidth(2, 110)
        self._metadata_table.setMaximumHeight(160)
        layout.addWidget(self._metadata_table)
        return self._grp_metadata

    def _build_action_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        self._btn_start = QPushButton(self._tr("btn_start"))
        self._btn_start.setDefault(True)
        self._btn_cancel = QPushButton(self._tr("btn_cancel"))
        self._btn_cancel.setEnabled(False)
        bar.addStretch()
        bar.addWidget(self._btn_start)
        bar.addWidget(self._btn_cancel)
        return bar

    def _build_progress_group(self) -> QGroupBox:
        self._grp_progress = QGroupBox(self._tr("group_progress"))
        layout = QVBoxLayout(self._grp_progress)

        self._lbl_overall = QLabel(self._tr("lbl_overall"))
        layout.addWidget(self._lbl_overall)
        self._progress_overall = QProgressBar()
        self._progress_overall.setValue(0)
        layout.addWidget(self._progress_overall)

        self._step_label = QLabel(self._tr("lbl_current_step"))
        layout.addWidget(self._step_label)
        self._progress_step = QProgressBar()
        self._progress_step.setRange(0, 100)
        self._progress_step.setValue(0)
        layout.addWidget(self._progress_step)
        return self._grp_progress

    def _build_log_group(self) -> QGroupBox:
        self._grp_log = QGroupBox(self._tr("group_log"))
        layout = QVBoxLayout(self._grp_log)
        self._log_area = QTextEdit()
        self._log_area.setReadOnly(True)
        self._log_area.setFontFamily("Menlo, Monaco, monospace")
        layout.addWidget(self._log_area)
        return self._grp_log

    # ------------------------------------------------------------------
    # Signal connections
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        self._btn_add.clicked.connect(self._on_add_files_clicked)
        self._btn_remove.clicked.connect(self._on_remove_selected)
        self._btn_browse.clicked.connect(self._on_browse_output)
        self._btn_browse_whisper_bin.clicked.connect(self._on_browse_whisper_bin)
        self._btn_browse_whisper_model.clicked.connect(self._on_browse_whisper_model)
        self._btn_start.clicked.connect(self._on_start)
        self._btn_cancel.clicked.connect(self._on_cancel)
        self._lang_combo.currentIndexChanged.connect(self._on_language_changed)

    # ------------------------------------------------------------------
    # File management
    # ------------------------------------------------------------------

    def _on_add_files_clicked(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            self._tr("dlg_select_audio"),
            str(Path.home()),
            self._tr("dlg_audio_filter"),
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
            self, self._tr("dlg_select_output_folder"), self._output_dir_edit.text()
        )
        if directory:
            self._output_dir_edit.setText(directory)

    def _on_browse_whisper_bin(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            self._tr("dlg_select_whisper_bin"),
            self._whisper_bin_edit.text() or str(Path.home()),
        )
        if path:
            self._whisper_bin_edit.setText(path)

    def _on_browse_whisper_model(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            self._tr("dlg_select_whisper_model"),
            self._whisper_model_edit.text() or str(Path.home()),
            self._tr("dlg_model_filter"),
        )
        if path:
            self._whisper_model_edit.setText(path)

    def _update_start_button(self) -> None:
        self._btn_start.setEnabled(self._file_list.count() > 0)

    # ------------------------------------------------------------------
    # Pipeline start / cancel
    # ------------------------------------------------------------------

    def _build_current_config(self) -> dict:
        """Build a config dict from the current GUI field values."""
        return {
            **self._config,
            "ffmpeg_path": self._ffmpeg_path_edit.text().strip() or "ffmpeg",
            "whisper_cpp_path": self._whisper_bin_edit.text().strip(),
            "whisper_model_path": self._whisper_model_edit.text().strip(),
            "ollama_model": self._ollama_model_edit.text().strip(),
            "output_dir": self._output_dir_edit.text(),
            "last_mode": self._mode_combo.currentIndex() + 1,
            "language": self._lang,
        }

    def _on_start(self) -> None:
        mode = self._mode_combo.currentIndex() + 1
        output_dir = Path(self._output_dir_edit.text())
        config = self._build_current_config()

        try:
            validate_dependencies(config, mode)
        except RuntimeError as exc:
            QMessageBox.critical(self, self._tr("dlg_dep_error_title"), str(exc))
            return

        inputs: list[PipelineInput] = []
        for i in range(self._file_list.count()):
            path_str = self._file_list.item(i).data(Qt.ItemDataRole.UserRole)
            file_path = Path(path_str)
            title = (
                self._metadata_table.item(i, 1) or QTableWidgetItem(file_path.stem)
            ).text().strip() or file_path.stem
            date = (self._metadata_table.item(i, 2) or QTableWidgetItem("")).text().strip()
            inputs.append(
                PipelineInput(
                    file_path=file_path,
                    title=title,
                    date=date,
                    mode=mode,
                    config=config,
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
        self._log_area.append(f"— {self._tr('log_cancel')} —")

    # ------------------------------------------------------------------
    # Worker signal handlers
    # ------------------------------------------------------------------

    def _on_file_started(self, index: int, name: str) -> None:
        total = self._progress_overall.maximum()
        self._progress_overall.setValue(index)
        self._log_area.append(f"\n[{index + 1}/{total}] {self._tr('log_processing')}: {name}")

    def _on_progress_updated(self, msg: str) -> None:
        self._step_label.setText(f"{self._tr('lbl_current_step')} {msg}")

    def _on_log_message(self, msg: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_area.append(f"[{ts}] {msg}")

    def _on_file_completed(self, index: int, output_path: Path) -> None:
        self._progress_overall.setValue(index + 1)
        self._log_area.append(f"✓ {self._tr('log_saved')}: {output_path}")

    def _on_pipeline_finished(self) -> None:
        self._progress_step.setRange(0, 100)
        self._progress_step.setValue(100)
        self._step_label.setText(f"{self._tr('lbl_current_step')} {self._tr('lbl_done')}")
        self._btn_start.setEnabled(True)
        self._btn_cancel.setEnabled(False)
        self._log_area.append(f"\n✓ {self._tr('log_all_done')}")
        QMessageBox.information(self, self._tr("dlg_done_title"), self._tr("dlg_done_body"))
        self._try_notify(self._tr("dlg_done_body"))

    def _on_error_occurred(self, message: str) -> None:
        self._progress_step.setRange(0, 100)
        self._progress_step.setValue(0)
        self._step_label.setText(f"{self._tr('lbl_current_step')} {self._tr('lbl_error')}")
        self._btn_start.setEnabled(True)
        self._btn_cancel.setEnabled(False)
        self._log_area.append(f"\n✗ {self._tr('log_error')}: {message}")
        QMessageBox.critical(self, self._tr("dlg_pipeline_error_title"), message)

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
                tray.showMessage(self._tr("window_title"), message)
        except Exception:  # pylint: disable=broad-except
            pass

    # ------------------------------------------------------------------
    # Config persistence on close
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait(3000)

        updated = self._build_current_config()
        try:
            save_config(_CONFIG_PATH, updated)
        except OSError:
            pass
        super().closeEvent(event)
