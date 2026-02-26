"""Tests for setup wizard and first-launch detection."""
from __future__ import annotations

from pathlib import Path

import pytest

from localmeetingtranscriber.gui.app import _needs_setup
from localmeetingtranscriber.gui.setup_wizard import (
    WHISPER_MODELS,
    _DEFAULT_MODEL_INDEX,
    SetupWizard,
)


# ---------------------------------------------------------------------------
# _needs_setup
# ---------------------------------------------------------------------------

def test_needs_setup_when_config_empty():
    assert _needs_setup({}) is True


def test_needs_setup_when_paths_missing():
    config = {
        "whisper_cpp_path": "/nonexistent/whisper",
        "whisper_model_path": "/nonexistent/model.bin",
    }
    assert _needs_setup(config) is True


def test_needs_setup_false_when_both_files_exist(tmp_path):
    bin_file = tmp_path / "whisper"
    bin_file.touch()
    model_file = tmp_path / "model.bin"
    model_file.touch()
    config = {
        "whisper_cpp_path": str(bin_file),
        "whisper_model_path": str(model_file),
    }
    assert _needs_setup(config) is False


def test_needs_setup_true_when_only_binary_exists(tmp_path):
    bin_file = tmp_path / "whisper"
    bin_file.touch()
    config = {
        "whisper_cpp_path": str(bin_file),
        "whisper_model_path": "/nonexistent/model.bin",
    }
    assert _needs_setup(config) is True


def test_needs_setup_true_when_only_model_exists(tmp_path):
    model_file = tmp_path / "model.bin"
    model_file.touch()
    config = {
        "whisper_cpp_path": "/nonexistent/whisper",
        "whisper_model_path": str(model_file),
    }
    assert _needs_setup(config) is True


# ---------------------------------------------------------------------------
# WHISPER_MODELS catalogue
# ---------------------------------------------------------------------------

def test_whisper_models_has_entries():
    assert len(WHISPER_MODELS) >= 3


def test_default_model_index_is_small():
    filename, _, _ = WHISPER_MODELS[_DEFAULT_MODEL_INDEX]
    assert "small" in filename


def test_each_model_entry_has_three_fields():
    for entry in WHISPER_MODELS:
        assert len(entry) == 3, f"Expected (filename, label, size_mb), got {entry}"


# ---------------------------------------------------------------------------
# SetupWizard creation
# ---------------------------------------------------------------------------

def test_wizard_creates_five_pages(qtbot):
    wizard = SetupWizard({})
    qtbot.addWidget(wizard)
    assert wizard.pageIds().__len__() == 5


def test_wizard_updated_config_contains_language(qtbot):
    wizard = SetupWizard({"language": "zh-TW"})
    qtbot.addWidget(wizard)
    cfg = wizard.updated_config()
    assert cfg.get("language") == "zh-TW"


def test_wizard_updated_config_merges_existing_keys(qtbot):
    wizard = SetupWizard({"ollama_model": "llama3"})
    qtbot.addWidget(wizard)
    cfg = wizard.updated_config()
    assert cfg.get("ollama_model") == "llama3"
