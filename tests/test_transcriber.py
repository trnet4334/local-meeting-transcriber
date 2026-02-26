
def test_build_whisper_cmd():
    from localmeetingtranscriber.transcriber import build_whisper_cmd

    cmd = build_whisper_cmd("./whisper.cpp/main", "model.bin", "audio.wav", "out")
    assert "--output-srt" in cmd
    assert "-m" in cmd
