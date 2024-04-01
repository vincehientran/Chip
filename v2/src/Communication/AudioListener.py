import pyaudio
import threading
import numpy as np
import time
import logging

class AudioListener:
    '''
    AudioListener can be used to detect audio from microphone using pyaudio
    
    example usage
    al = AudioListener()
    al.start_listening()
    counter = 0
    while counter < 20:
        print(al.sound_detected())
        time.sleep(1)
        counter += 1

    al.stop_listening()
    '''

    def __init__(self) -> None:
        '''Initialize AudioListener'''
        self.CHUNK = 4096
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.THRESHOLD = 20  # Adjust this threshold as needed

        self.p = pyaudio.PyAudio()
        self.is_loud = threading.Event()
        self.is_listening = threading.Event()

        self.lock = threading.Event()

        self.stream = None
        self.audio_thread = None

        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)

    def sound_detected(self) -> bool:
        '''
        Check if sound is currently detected.

        Returns:
            bool: True if sound is detected, False otherwise.
        '''

        if not self.is_listening.is_set():
            self.logger.warning('AudioListener is not listening')
        return self.is_loud.is_set()

    def start_listening(self) -> None:
        '''Start listening for audio.'''

        if self.is_listening.is_set():
            self.logger.warning('AudioListener is already listening')
            return

        self.is_listening.set()
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )

        self.audio_thread = threading.Thread(target=self.__private_capture_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()

    def stop_listening(self) -> None:
        '''Stop listening for audio.'''

        if not self.is_listening.is_set():
            self.logger.warning('AudioListener is already not listening')
            return

        self.lock.set() 
        self.is_listening.clear() 

        timeout = time.time() + 5 
        while self.lock.is_set() and time.time() < timeout:
            time.sleep(0.3)

        if self.lock.is_set():
            self.logger.warning('capture_audio never unlocked')

        self.lock.clear()

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.audio_thread.join()

    def __private_capture_audio(self) -> None:
        '''
        Captures and processes the audio. 
        Sets the boolean flag for if audio is detected or not
        '''

        while self.is_listening.is_set():
            data = np.frombuffer(self.stream.read(self.CHUNK), dtype=np.int16)
            rms = np.sqrt(np.mean(np.square(data)))
            if rms > self.THRESHOLD:
                self.is_loud.set()
            else:
                self.is_loud.clear()

        self.lock.clear()
