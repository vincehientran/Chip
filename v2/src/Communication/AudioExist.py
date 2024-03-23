import pyaudio
import threading
import numpy as np
import time


def capture_audio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    THRESHOLD = 20  # Adjust this threshold as needed

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    while True:
        data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        rms = np.sqrt(np.mean(np.square(data)))
        if rms > THRESHOLD:
            is_loud.set()  
        else:
            is_loud.clear()  

    # stream.stop_stream()
    # stream.close()
    # p.terminate()

is_loud = threading.Event()


audio_thread = threading.Thread(target=capture_audio)
audio_thread.daemon = True  # Set the thread as a daemon so it will exit when the main thread exits
audio_thread.start()

while True:
    if is_loud.is_set():
        print("Loud audio detected")
    else:
        print("No loud audio")
    time.sleep(0.1)
