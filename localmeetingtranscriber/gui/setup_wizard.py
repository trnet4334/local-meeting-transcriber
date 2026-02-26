"""First-launch setup wizard for LocalMeetingTranscriber.

Pages
-----
1. WelcomePage      — introduction, no input required
2. WhisperBinaryPage — locate whisper.cpp executable (blocks Next if missing)
3. ModelDownloadPage — download or locate .bin model (blocks Next if missing)
4. OllamaPage        — check Ollama status (optional, never blocks Next)
5. FinishPage        — summary
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QComboBox,
    QVBoxLayout,
    QWizard,
    QWizardPage,
)

from localmeetingtranscriber.pipeline import PROJECT_ROOT
from localmeetingtranscriber.gui.downloader import ModelDownloader
from localmeetingtranscriber.gui.i18n import DEFAULT_LANGUAGE, TRANSLATIONS
from localmeetingtranscriber.transcriber import detect_whisper_type

# ---------------------------------------------------------------------------
# Whisper model catalogue
# ---------------------------------------------------------------------------

#: (filename, display_label, approx_size_mb)
WHISPER_MODELS: list[tuple[str, str, int]] = [
    ("ggml-tiny.bin",           "Tiny        — fastest, lower accuracy  (~75 MB)",    75),
    ("ggml-base.bin",           "Base        — fast, decent accuracy    (~142 MB)",  142),
    ("ggml-small.bin",          "Small       — good balance  (default)  (~466 MB)",  466),
    ("ggml-medium.bin",         "Medium      — better accuracy          (~1.5 GB)", 1500),
    ("ggml-large-v3-q5_0.bin",  "Large-v3 Q5 — best accuracy           (~1.1 GB)", 1100),
]

# Default model index (small)
_DEFAULT_MODEL_INDEX = 2

HF_BASE_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main"


# ---------------------------------------------------------------------------
# Page 1 — Welcome
# ---------------------------------------------------------------------------

class _WelcomePage(QWizardPage):
    def __init__(self, tr) -> None:
        super().__init__()
        self.setTitle(tr("wizard_welcome_title"))
        self.setSubTitle(tr("wizard_welcome_subtitle"))

        body = QLabel(tr("wizard_welcome_body"))
        body.setWordWrap(True)
        body.setTextFormat(Qt.TextFormat.PlainText)

        layout = QVBoxLayout(self)
        layout.addWidget(body)
        layout.addStretch()


# ---------------------------------------------------------------------------
# Page 2 — whisper.cpp binary
# ---------------------------------------------------------------------------

class _WhisperBinaryPage(QWizardPage):
    def __init__(self, tr, config: dict) -> None:
        super().__init__()
        self._tr = tr
        self._config = config

        self.setTitle(tr("wizard_binary_title"))
        self.setSubTitle(tr("wizard_binary_subtitle"))

        self._status_label = QLabel()

        self._path_edit = QLineEdit()
        self._path_edit.setPlaceholderText(tr("wizard_binary_placeholder"))
        self._path_edit.textChanged.connect(self._on_path_changed)

        self._btn_browse = QPushButton(tr("btn_browse"))
        self._btn_browse.clicked.connect(self._on_browse)

        path_row = QHBoxLayout()
        path_row.addWidget(QLabel(tr("wizard_binary_path_label")))
        path_row.addWidget(self._path_edit, 1)
        path_row.addWidget(self._btn_browse)

        layout = QVBoxLayout(self)
        layout.addWidget(self._status_label)
        layout.addSpacing(10)
        layout.addLayout(path_row)
        layout.addStretch()

    def initializePage(self) -> None:
        path = self._config.get("whisper_cpp_path", "")
        self._path_edit.setText(path)
        self._refresh_status(path)

    def isComplete(self) -> bool:
        path = self._path_edit.text().strip()
        if not path or not Path(path).is_file():
            return False
        # Block openai-whisper — this app requires whisper.cpp
        return detect_whisper_type(path) != "openai-whisper"

    def _on_path_changed(self, text: str) -> None:
        stripped = text.strip()
        self._config["whisper_cpp_path"] = stripped
        self._refresh_status(stripped)
        self.completeChanged.emit()

    def _on_browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            self._tr("dlg_select_whisper_bin"),
            self._path_edit.text().strip() or str(Path.home()),
        )
        if path:
            self._path_edit.setText(path)

    def _refresh_status(self, path: str) -> None:
        path = path.strip()
        if not path or not Path(path).is_file():
            self._status_label.setText(self._tr("wizard_binary_status_missing"))
            self._status_label.setStyleSheet("color: #c0392b;")
            return

        backend = detect_whisper_type(path)
        if backend == "openai-whisper":
            self._status_label.setText(
                "✗  This is the openai-whisper Python package — whisper.cpp is required.\n"
                "   Install from: https://github.com/ggerganov/whisper.cpp"
            )
            self._status_label.setStyleSheet("color: #c0392b;")
        elif backend == "whisper.cpp":
            self._status_label.setText(
                f"{self._tr('wizard_binary_status_ok')}  (whisper.cpp)"
            )
            self._status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            # Unknown but file exists — allow through with a caution note
            self._status_label.setText(
                f"{self._tr('wizard_binary_status_ok')}  ⚠ type could not be verified"
            )
            self._status_label.setStyleSheet("color: #e67e22; font-weight: bold;")


# ---------------------------------------------------------------------------
# Page 3 — Model download / locate
# ---------------------------------------------------------------------------

class _ModelDownloadPage(QWizardPage):
    def __init__(self, tr, config: dict) -> None:
        super().__init__()
        self._tr = tr
        self._config = config
        self._downloader: ModelDownloader | None = None

        self.setTitle(tr("wizard_model_title"))
        self.setSubTitle(tr("wizard_model_subtitle"))

        # ── Status ──────────────────────────────────────────────────────
        self._status_label = QLabel()

        # ── Model selector ──────────────────────────────────────────────
        self._model_combo = QComboBox()
        for filename, display, _ in WHISPER_MODELS:
            self._model_combo.addItem(display, filename)
        self._model_combo.setCurrentIndex(_DEFAULT_MODEL_INDEX)

        # ── Download-to folder ──────────────────────────────────────────
        default_dl_dir = str(PROJECT_ROOT / "models")
        self._save_dir_edit = QLineEdit(default_dl_dir)
        self._btn_browse_dir = QPushButton(tr("btn_browse"))
        self._btn_browse_dir.clicked.connect(self._on_browse_dir)

        # ── Action buttons ──────────────────────────────────────────────
        self._btn_download = QPushButton(tr("wizard_model_btn_download"))
        self._btn_download.clicked.connect(self._on_download)

        self._btn_locate = QPushButton(tr("wizard_model_btn_locate"))
        self._btn_locate.clicked.connect(self._on_locate)

        self._btn_cancel_dl = QPushButton(tr("wizard_model_cancel"))
        self._btn_cancel_dl.clicked.connect(self._on_cancel_download)
        self._btn_cancel_dl.setVisible(False)

        # ── Progress ────────────────────────────────────────────────────
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)

        self._progress_label = QLabel()
        self._progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._progress_label.setVisible(False)

        # ── Layout ──────────────────────────────────────────────────────
        layout = QVBoxLayout(self)
        layout.addWidget(self._status_label)
        layout.addSpacing(10)

        # Model row
        model_row = QHBoxLayout()
        model_row.addWidget(QLabel(tr("wizard_model_select_label")))
        model_row.addWidget(self._model_combo, 1)
        layout.addLayout(model_row)

        # Save-dir row
        dir_row = QHBoxLayout()
        dir_row.addWidget(QLabel(tr("wizard_model_save_to_label")))
        dir_row.addWidget(self._save_dir_edit, 1)
        dir_row.addWidget(self._btn_browse_dir)
        layout.addLayout(dir_row)

        layout.addSpacing(8)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self._btn_download)
        btn_row.addWidget(self._btn_locate)
        btn_row.addWidget(self._btn_cancel_dl)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        layout.addSpacing(6)
        layout.addWidget(self._progress_bar)
        layout.addWidget(self._progress_label)
        layout.addStretch()

    # ------------------------------------------------------------------
    # QWizardPage overrides
    # ------------------------------------------------------------------

    def initializePage(self) -> None:
        model_path = self._config.get("whisper_model_path", "")
        if model_path and Path(model_path).parent.is_dir():
            self._save_dir_edit.setText(str(Path(model_path).parent))
        self._refresh_status(model_path)

    def isComplete(self) -> bool:
        model_path = self._config.get("whisper_model_path", "")
        return bool(model_path) and Path(model_path).is_file()

    def cleanupPage(self) -> None:
        """Cancel any running download when the user clicks Back."""
        self._cancel_if_running()
        self._set_downloading(False)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_browse_dir(self) -> None:
        d = QFileDialog.getExistingDirectory(
            self, self._tr("wizard_model_dl_dir_title"), self._save_dir_edit.text()
        )
        if d:
            self._save_dir_edit.setText(d)

    def _on_locate(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            self._tr("dlg_select_whisper_model"),
            self._save_dir_edit.text(),
            self._tr("dlg_model_filter"),
        )
        if path:
            self._config["whisper_model_path"] = path
            self._refresh_status(path)

    def _on_download(self) -> None:
        filename: str = self._model_combo.currentData()
        save_dir = Path(self._save_dir_edit.text().strip())
        if not save_dir:
            save_dir = PROJECT_ROOT / "models"
        dest = save_dir / filename
        url = f"{HF_BASE_URL}/{filename}"

        self._downloader = ModelDownloader(url, dest)
        self._downloader.progress.connect(self._on_dl_progress)
        self._downloader.finished.connect(self._on_dl_finished)
        self._downloader.error.connect(self._on_dl_error)

        self._set_downloading(True)
        self._progress_bar.setValue(0)
        self._progress_label.setText(self._tr("wizard_model_downloading"))
        self._downloader.start()

    def _on_cancel_download(self) -> None:
        self._cancel_if_running()
        self._set_downloading(False)

    def _on_dl_progress(self, downloaded: int, total: int) -> None:
        if total > 0:
            self._progress_bar.setRange(0, total)
            self._progress_bar.setValue(downloaded)
            pct = downloaded * 100 // total
            mb_dl = downloaded / 1_048_576
            mb_total = total / 1_048_576
            self._progress_label.setText(f"{mb_dl:.1f} / {mb_total:.1f} MB  ({pct}%)")
        else:
            self._progress_bar.setRange(0, 0)  # indeterminate

    def _on_dl_finished(self, path: Path) -> None:
        self._downloader = None
        self._set_downloading(False)
        # Auto-set model path — no manual config editing needed
        self._config["whisper_model_path"] = str(path)
        self._refresh_status(str(path))

    def _on_dl_error(self, msg: str) -> None:
        self._downloader = None
        self._set_downloading(False)
        QMessageBox.critical(self, self._tr("wizard_model_dl_error_title"), msg)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _refresh_status(self, model_path: str) -> None:
        if model_path and Path(model_path).is_file():
            self._status_label.setText(self._tr("wizard_model_status_ok"))
            self._status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self._status_label.setText(self._tr("wizard_model_status_missing"))
            self._status_label.setStyleSheet("color: #e67e22;")
        self.completeChanged.emit()

    def _set_downloading(self, active: bool) -> None:
        self._btn_download.setEnabled(not active)
        self._btn_locate.setEnabled(not active)
        self._model_combo.setEnabled(not active)
        self._save_dir_edit.setReadOnly(active)
        self._btn_browse_dir.setEnabled(not active)
        self._btn_cancel_dl.setVisible(active)
        self._progress_bar.setVisible(active)
        self._progress_label.setVisible(active)
        if not active:
            self._progress_bar.setRange(0, 100)

    def _cancel_if_running(self) -> None:
        if self._downloader and self._downloader.isRunning():
            self._downloader.cancel()
            self._downloader.wait(5000)
        self._downloader = None


# ---------------------------------------------------------------------------
# Page 4 — Ollama (optional)
# ---------------------------------------------------------------------------

class _OllamaPage(QWizardPage):
    def __init__(self, tr) -> None:
        super().__init__()
        self._tr = tr

        self.setTitle(tr("wizard_ollama_title"))
        self.setSubTitle(tr("wizard_ollama_subtitle"))

        self._status_label = QLabel()

        note = QLabel(tr("wizard_ollama_note"))
        note.setWordWrap(True)
        note.setTextFormat(Qt.TextFormat.PlainText)

        self._btn_check = QPushButton(tr("wizard_ollama_btn_check"))
        self._btn_check.clicked.connect(self._check_ollama)

        self._btn_open = QPushButton(tr("wizard_ollama_btn_open"))
        self._btn_open.clicked.connect(self._open_site)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self._btn_check)
        btn_row.addWidget(self._btn_open)
        btn_row.addStretch()

        layout = QVBoxLayout(self)
        layout.addWidget(self._status_label)
        layout.addSpacing(10)
        layout.addWidget(note)
        layout.addSpacing(8)
        layout.addLayout(btn_row)
        layout.addStretch()

    def initializePage(self) -> None:
        self._check_ollama()

    def isComplete(self) -> bool:
        return True  # optional; never blocks Next

    def _check_ollama(self) -> None:
        if self._ping_ollama():
            self._status_label.setText(self._tr("wizard_ollama_status_ok"))
            self._status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self._status_label.setText(self._tr("wizard_ollama_status_missing"))
            self._status_label.setStyleSheet("color: #e67e22;")

    @staticmethod
    def _ping_ollama() -> bool:
        try:
            urllib.request.urlopen("http://localhost:11434", timeout=2)
            return True
        except Exception:
            return False

    def _open_site(self) -> None:
        QDesktopServices.openUrl(QUrl("https://ollama.ai"))


# ---------------------------------------------------------------------------
# Page 5 — Finish
# ---------------------------------------------------------------------------

class _FinishPage(QWizardPage):
    def __init__(self, tr) -> None:
        super().__init__()
        self.setTitle(tr("wizard_finish_title"))
        self.setSubTitle(tr("wizard_finish_subtitle"))

        body = QLabel(tr("wizard_finish_body"))
        body.setWordWrap(True)
        body.setTextFormat(Qt.TextFormat.PlainText)

        layout = QVBoxLayout(self)
        layout.addWidget(body)
        layout.addStretch()


# ---------------------------------------------------------------------------
# SetupWizard
# ---------------------------------------------------------------------------

class SetupWizard(QWizard):
    """Multi-page first-launch wizard.

    Parameters
    ----------
    config:
        The current application config dict.  The wizard works on a mutable
        copy; call ``updated_config()`` after the wizard closes to retrieve
        the merged result.
    """

    def __init__(self, config: dict, parent=None) -> None:
        super().__init__(parent)
        self._config = dict(config)
        lang = config.get("language", DEFAULT_LANGUAGE)
        self._lang = lang if lang in TRANSLATIONS else DEFAULT_LANGUAGE

        self.setWindowTitle(self._tr("wizard_title"))
        self.setMinimumSize(640, 500)

        if sys.platform == "darwin":
            self.setWizardStyle(QWizard.WizardStyle.MacStyle)
        else:
            self.setWizardStyle(QWizard.WizardStyle.ModernStyle)

        # Keep a reference to model page so reject() can clean it up
        self._model_page = _ModelDownloadPage(self._tr, self._config)

        self.addPage(_WelcomePage(self._tr))
        self.addPage(_WhisperBinaryPage(self._tr, self._config))
        self.addPage(self._model_page)
        self.addPage(_OllamaPage(self._tr))
        self.addPage(_FinishPage(self._tr))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def updated_config(self) -> dict:
        """Return the config dict with all wizard-collected values merged in."""
        return dict(self._config)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _tr(self, key: str) -> str:
        return (
            TRANSLATIONS.get(self._lang, TRANSLATIONS[DEFAULT_LANGUAGE]).get(key)
            or TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key)
        )

    def reject(self) -> None:
        """Ensure any running download is cleaned up before closing."""
        self._model_page._cancel_if_running()
        super().reject()
