
def test_build_ffmpeg_cmd():
    from localmeetingtranscriber.converter import build_ffmpeg_cmd

    cmd = build_ffmpeg_cmd("ffmpeg", "in.m4a", "out.wav")
    assert cmd[:2] == ["ffmpeg", "-y"]
    assert "-ar" in cmd
    assert "16000" in cmd
