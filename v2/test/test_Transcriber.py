import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from Communication.Transcriber import Transcriber

@pytest.fixture
def transcriber():
    return Transcriber('tiny.en')

def test_init_valid_model_type(transcriber):
    # Test initialization with a valid modelType
    assert isinstance(transcriber, Transcriber)
    assert transcriber.modelType == 'tiny.en'

def test_init_invalid_model_type():
    # Test initialization with an invalid modelType throws ValueError
    with pytest.raises(ValueError):
        Transcriber('invalid_model_type')

def test_transcribe(transcriber):
    # Check if the transcribed text is a non-empty string
    script_dir = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(script_dir, '..', 'res', 'audio.mp3')

    transcribed_text = transcriber.transcribe(audio_path)

    assert isinstance(transcribed_text, str)
    assert transcribed_text.strip() 