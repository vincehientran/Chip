import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from Communication.AudioListener import AudioListener  # Replace 'your_module' with the actual module name

@pytest.fixture
def audio_listener():
    return AudioListener()

def test_start_listening(audio_listener):
    # Ensure start_listening sets is_listening flag
    audio_listener.start_listening()
    assert audio_listener.is_listening.is_set()

def test_stop_listening(audio_listener):
    # Ensure stop_listening clears is_listening flag
    audio_listener.start_listening()
    audio_listener.stop_listening()
    assert not audio_listener.is_listening.is_set()

def test_sound_detected(audio_listener):
    # Ensure sound_detected returns False initially
    assert not audio_listener.sound_detected()

    # Simulate sound detected
    audio_listener.is_loud.set()
    assert audio_listener.sound_detected()

    # Simulate no sound detected
    audio_listener.is_loud.clear()
    assert not audio_listener.sound_detected()
