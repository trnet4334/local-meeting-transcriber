"""QApplication entry point for LocalMeetingTranscriber GUI."""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from localmeetingtranscriber.config import load_config, save_config
from localmeetingtranscriber.pipeline import PROJECT_ROOT
from localmeetingtranscriber.gui.main_window import MainWindow
from localmeetingtranscriber.gui.setup_wizard import SetupWizard

_CONFIG_PATH = PROJECT_ROOT / "config.json"


def _needs_setup(config: dict) -> bool:
    """Return True when the setup wizard should run.

    The wizard is shown whenever the whisper.cpp binary or model file
    configured in *config* does not exist on disk.  This covers both
    first-time runs and cases where the user moved the files.
    """
    whisper_bin = config.get("whisper_cpp_path", "")
    model_path = config.get("whisper_model_path", "")
    bin_ok = bool(whisper_bin) and Path(whisper_bin).is_file()
    model_ok = bool(model_path) and Path(model_path).is_file()
    return not (bin_ok and model_ok)


def main() -> None:
    """Launch the GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("LocalMeetingTranscriber")
    app.setApplicationVersion("0.2.0")

    config = load_config(_CONFIG_PATH)

    if _needs_setup(config):
        wizard = SetupWizard(config)
        wizard.exec()  # Accepted or Rejected — always collect what was entered
        config = wizard.updated_config()
        try:
            save_config(_CONFIG_PATH, config)
        except OSError:
            pass

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
