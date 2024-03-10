import os
import queue
import sys
import time

import sounddevice as sd
import soundfile as sf
import wave
import threading
import librosa
from detect_pi import is_raspberrypi, raspberrypi_version
import numpy  # Make sure NumPy is loaded before it is used in the callback

assert numpy  # avoid "imported but unused" message (W0611)
from pydub import AudioSegment, effects


class AudioRecorder:
    def __init__(self, rpi_execution: bool = False):
        self.recording = None
        self.rpi = False
        self.samplerate = 44100
        self.block_size = 1024
        self.channels = 1
        self.duration = 5
        if rpi_execution:
            print("RPI execution")
            rpi_version = raspberrypi_version()
            match rpi_version:
                case 4:
                    from gpio_class_rpigpio import gpio_class
                    self.gpio = gpio_class(callback_function=self.adapt_recording)
                case 5:
                    from gpio_class_gpiozero import gpio_class
                    self.gpio = gpio_class(callback_function_pressed=self.start_recording,
                                           callback_function_released=self.stop_recording)
                case _:
                    print("check which gpio class to use for this rpi {}".format(rpi_version))
                    from gpio_class_gpiozero import gpio_class
                    self.gpio = gpio_class(callback_function_pressed=self.start_recording,
                                           callback_function_released=self.stop_recording)
            self.rpi = True
        else:
            print("running on reg pc")
            from pynput import keyboard
            listener = keyboard.Listener(
                on_press=self.alter_recording_key
            )
            listener.start()

        # Audio parameters
        sd.default.samplerate = self.samplerate
        sd.default.blocksize = self.block_size
        sd.default.channels = self.channels
        # sd.default.dtype = 'int24'
        sd.default.device = 'USB Audio Device'
        self.q = queue.Queue()

        # recording files
        self.frames = []

        self.latest_recording = ""

    def adapt_recording(self, channel):
        """used only for rpi4 & RPI.GPIO library"""
        time.sleep(0.1)
        if GPIO.input(channel) == GPIO.LOW:
            self.start_recording()
        else:
            self.stop_recording()

    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block. This puts the audio in a queue so we can
        save it in the main thread"""
        #        print(indata)
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())

    def alter_recording_key(self, key):
        """function used when we use a keyboard"""
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
            # we calculate the timeout time
            timeout = time.time() + self.duration
            with sf.SoundFile(file_name, mode='x', samplerate=self.samplerate, channels=self.channels,
                              subtype="PCM_24") as file:
                with sd.InputStream(callback=self.callback):
                    # debug LEDs, this may be removed if not wanted
                    if self.rpi:
                        self.gpio.switch_led(to_green=True)
                    # debug text, this may be removed if not wanted
                    print('#' * 80)
                    print('press Ctrl+C to stop the recording')
                    print('#' * 80)
                    # keep recording until the button is pushed or the timeout has happened
                    while self.recording and time.time() <= timeout:
                        file.write(self.q.get())
            # normalize the audio
            raw_sound = AudioSegment.from_file(file_name, "wav")
            normalized_sound = effects.normalize(raw_sound)
            normalized_sound.export(file_name, format="wav")
        except sd.PortAudioError as e:
            print("PA error {}".format(e))
            # try again, miserable portaudio library
            self.record_audio()

        self.latest_recording = file_name

        # play audio after recording
        # TODO KASPER, remove this if you want to hook up espeak
        self.play_audio(self.latest_recording)

    def play_audio(self, audio_file):
        try:
            data, fs = sf.read(audio_file)
            sd.play(data, fs)
            sd.wait()
        except sd.PortAudioError as e:
            print("PA error {}".format(e))
            # try again, miserable portaudio library
            self.play_audio(audio_file)


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