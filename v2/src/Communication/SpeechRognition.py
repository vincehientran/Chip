import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np

class AudioRecorder:
    def __init__(self):
        self.sampling_frequency = 44100

    def record(self, seconds: int = 10):
        audio_data = sd.rec(int(seconds * self.sampling_frequency), samplerate=self.sampling_frequency, channels=1, dtype='float64')
        sd.wait()
        return audio_data

    def save_as_wav(self, audio_data, filename):
        wav.write(filename, self.sampling_frequency, np.asarray(audio_data))

if __name__ == "__main__":
    recorder = AudioRecorder()
    audio_data = recorder.record()
    recorder.save_as_wav(audio_data, "recorded_audio.wav")
