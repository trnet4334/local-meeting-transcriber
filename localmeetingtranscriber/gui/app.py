"""QApplication entry point for LocalMeetingTranscriber GUI."""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from localmeetingtranscriber.gui.main_window import MainWindow


def main() -> None:
    """Launch the GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("LocalMeetingTranscriber")
    app.setApplicationVersion("0.2.0")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
