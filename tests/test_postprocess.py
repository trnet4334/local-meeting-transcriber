def test_srt_to_lines():
    from localmeetingtranscriber.postprocess import srt_to_lines

    srt = "1\n00:00:00,000 --> 00:00:02,000\nHello world\n"
    lines = srt_to_lines(srt)
    assert lines[0].startswith("[00:00:00]")
    assert "Hello world" in lines[0]
