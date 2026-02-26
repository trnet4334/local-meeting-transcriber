from pathlib import Path


def test_build_docx_path(tmp_path: Path):
    from localmeetingtranscriber.exporter import build_output_path

    path = build_output_path(tmp_path, "Meeting")
    assert str(path).endswith("Meeting.docx")
