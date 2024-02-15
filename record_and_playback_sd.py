import os
import queue
import sys
import time

import sounddevice as sd
import soundfile as sf
import wave
import threading
import librosa
from detect_pi import is_raspberrypi
import numpy  # Make sure NumPy is loaded before it is used in the callback

assert numpy  # avoid "imported but unused" message (W0611)
from gpio_class import gpio_class


class AudioRecorder:
    def __init__(self, rpi_execution: bool = False):
        self.recording = None
        self.rpi = False
        if rpi_execution:
            print("RPI execution")
            self.rpi = True
            self.gpio = gpio_class(callback_function=self.adapt_recording)
        else:
            print("running on reg pc")
            from pynput import keyboard
            listener = keyboard.Listener(
                on_press=self.alter_recording_key
            )
            listener.start()

        # Audio parameters
        sd.default.samplerate = 44100
        sd.default.blocksize = 1024
        sd.default.channels = 2
        # sd.default.dtype = 'int24'
        self.non_blocking = True

        self.q = queue.Queue()

        # recording files
        self.frames = []

        self.latest_recording = ""

    def adapt_recording(self, channel):
        time.sleep(0.1)
        if GPIO.input(channel) == GPIO.LOW:
            self.start_recording()
        else:
            self.stop_recording()

    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
#        print(indata)
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())

    def alter_recording_key(self, key):
        import pynput
        if type(key) == pynput.keyboard.KeyCode:
            if key.char == 'r':
                print("recording")
                self.start_recording()
            if key.char == 's':
                print("stopping")
                self.stop_recording()

    def start_recording(self):
        self.recording = True
        print("Recording started")

        self.gpio.switch_led(to_green=True)

        # Start recording in a separate thread
        threading.Thread(target=self.record_audio).start()

    def stop_recording(self):
        self.recording = False
        print("Recording stopped")
        self.gpio.switch_led(to_green=False)

    def record_audio(self):
        # Generate filename with timestamp
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        file_name = os.path.join(os.getcwd(), "recordings", f"output_{timestamp}.wav")

        self.frames.clear()
        try:
            if self.non_blocking:
                with sf.SoundFile(file_name, mode='x', samplerate=44100, channels=2, subtype="PCM_24") as file:

                        with sd.InputStream(callback=self.callback):
                            print('#' * 80)
                            print('press Ctrl+C to stop the recording')
                            print('#' * 80)
                            while self.recording:
                                file.write(self.q.get())
            else:
                duration = 5  # seconds
                my_recording = sd.rec(int(duration * 44100), samplerate=44100, channels=2)
                sd.wait()
                sd.play(my_recording, 44100)
        except sd.PortAudioError as e:
            print("PA error {}".format(e))
            # try again, miserable portaudio library
            self.record_audio()

        self.latest_recording = file_name

        # play audio after recording
        self.play_audio()

    def play_audio(self):
        data, fs = sf.read(self.latest_recording)
        sd.play(data, fs)
        sd.wait()

if __name__ == "__main__":
    try:
        import RPi.GPIO as GPIO
    except:
        print("no rpi?")

    audio_recorder = AudioRecorder(is_raspberrypi())
    # audio_recorder.check_devices()
    print("Waiting for button press...")
    while True:
        time.sleep(0.1)
