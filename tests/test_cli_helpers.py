from pathlib import Path

import pytest


def test_parse_selection():
    from localmeetingtranscriber.main import parse_selection

    assert parse_selection("1,3", 5) == [0, 2]


def test_parse_selection_out_of_range():
    from localmeetingtranscriber.main import parse_selection

    with pytest.raises(ValueError):
        parse_selection("0", 5)


def test_mode_requires_ollama():
    from localmeetingtranscriber.main import mode_requires_ollama

    assert mode_requires_ollama(3) is True
    assert mode_requires_ollama(4) is True
    assert mode_requires_ollama(1) is False


def test_console_script_name():
    import tomllib

    data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["scripts"]["lmt"] == "localmeetingtranscriber.main:main"
