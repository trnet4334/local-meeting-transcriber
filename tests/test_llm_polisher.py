
def test_build_ollama_cmd():
    from localmeetingtranscriber.llm_polisher import build_ollama_cmd

    cmd = build_ollama_cmd("qwen2.5:7b-instruct-q4_K_M")
    assert cmd[:2] == ["ollama", "run"]
