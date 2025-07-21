import pytest
from speech_transcriber.transcript import transcribe

def test_transcribe_empty(tmp_path):
    # Create an empty dummy file
    empty = tmp_path / "silence.wav"
    empty.write_bytes(b"")
    result = transcribe(str(empty))
    assert isinstance(result, str)
    