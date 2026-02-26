from pathlib import Path


def test_config_loads_defaults(tmp_path):
    from localmeetingtranscriber.config import load_config

    cfg = load_config(config_path=tmp_path / "missing.json")
    assert "whisper_cpp_path" in cfg
    assert "whisper_model_path" in cfg
