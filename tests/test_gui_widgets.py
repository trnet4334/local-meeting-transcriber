"""Tests for MainWindow widget state management."""
from __future__ import annotations

from pathlib import Path

import pytest

from localmeetingtranscriber.gui.main_window import MainWindow


@pytest.fixture()
def window(qtbot):
    """Create a MainWindow, register it with qtbot, return it."""
    w = MainWindow()
    qtbot.addWidget(w)
    return w


def test_start_button_disabled_with_no_files(window):
    """Start button is disabled when no files are loaded."""
    assert not window._btn_start.isEnabled()


def test_start_button_enabled_after_adding_file(window, tmp_path):
    """Start button becomes enabled after at least one file is added."""
    f = tmp_path / "meeting.m4a"
    f.touch()
    window._add_files([str(f)])
    assert window._btn_start.isEnabled()


def test_add_files_populates_list_widget(window, tmp_path):
    """_add_files adds items to the file list."""
    files = [tmp_path / f"m{i}.m4a" for i in range(3)]
    for f in files:
        f.touch()
    window._add_files([str(f) for f in files])
    assert window._file_list.count() == 3


def test_add_files_populates_metadata_table(window, tmp_path):
    """_add_files inserts rows into the metadata table."""
    files = [tmp_path / f"m{i}.m4a" for i in range(2)]
    for f in files:
        f.touch()
    window._add_files([str(f) for f in files])
    assert window._metadata_table.rowCount() == 2


def test_add_files_skips_duplicates(window, tmp_path):
    """Adding the same file twice does not create a duplicate row."""
    f = tmp_path / "meeting.m4a"
    f.touch()
    window._add_files([str(f)])
    window._add_files([str(f)])
    assert window._file_list.count() == 1
    assert window._metadata_table.rowCount() == 1


def test_remove_selected_removes_file_and_table_row(window, tmp_path, qtbot):
    """Selecting and removing a file removes both the list item and table row."""
    files = [tmp_path / f"m{i}.m4a" for i in range(2)]
    for f in files:
        f.touch()
    window._add_files([str(f) for f in files])

    window._file_list.setCurrentRow(0)
    window._on_remove_selected()

    assert window._file_list.count() == 1
    assert window._metadata_table.rowCount() == 1


def test_mode_combo_has_four_options(window):
    """Mode combo box has exactly four entries."""
    assert window._mode_combo.count() == 4


def test_metadata_table_default_title_is_stem(window, tmp_path):
    """Default title in metadata table is the file stem."""
    f = tmp_path / "my_meeting_2026.m4a"
    f.touch()
    window._add_files([str(f)])
    title_item = window._metadata_table.item(0, 1)
    assert title_item is not None
    assert title_item.text() == "my_meeting_2026"


def test_cancel_button_disabled_initially(window):
    """Cancel button starts disabled."""
    assert not window._btn_cancel.isEnabled()
