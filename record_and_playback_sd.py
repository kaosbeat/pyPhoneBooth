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

            # # Define GPIO pins
            # self.GPIO_BUTTON = 27
            # self.GPIO_RED_LED = 24
            # self.GPIO_GREEN_LED = 23

            # # Set up GPIO
            # GPIO.setmode(GPIO.BCM)
            # GPIO.setup(self.GPIO_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            # GPIO.setup(self.GPIO_RED_LED, GPIO.OUT)
            # GPIO.setup(self.GPIO_GREEN_LED, GPIO.OUT)

            # # Set up button event detection
            # GPIO.add_event_detect(self.GPIO_BUTTON, GPIO.BOTH, callback=self.adapt_recording, bouncetime=300)
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
        self.non_blocking = False

        self.q = queue.Queue()

        # recording files
        self.frames = []

        self.latest_recording = ""

    # def switch_led(self, to_green: bool):
    # if self.rpi:
    # if to_green:
    # GPIO.output(self.GPIO_RED_LED, GPIO.HIGH)
    # GPIO.output(self.GPIO_GREEN_LED, GPIO.LOW)
    # else:
    # GPIO.output(self.GPIO_RED_LED, GPIO.LOW)
    # GPIO.output(self.GPIO_GREEN_LED, GPIO.HIGH)

    def adapt_recording(self, channel):
        time.sleep(0.1)
        if GPIO.input(channel) == GPIO.LOW:
            self.start_recording()
        else:
            self.stop_recording()

    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        print(indata)
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())

    def alter_recording_key(self, key: pynput.keyboard.KeyCode):
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
        if self.non_blocking:
            with sf.SoundFile(file_name, mode='x', samplerate=44100, channels=2, subtype="PCM_24") as file:
                try:
                    with sd.InputStream(callback=self.callback):
                        print('#' * 80)
                        print('press Ctrl+C to stop the recording')
                        print('#' * 80)
                        while self.recording:
                            file.write(self.q.get())
                except sd.PortAudioError as e:
                    print("PA error {}".format(e))
                    # try again, miserable portaudio library
                    self.record_audio()
        else:
            duration = 5  # seconds
            myrecording = sd.rec(int(duration * 44100), samplerate=44100, channels=2)
            sd.wait()
            sd.play(myrecording, 44100)

        self.latest_recording = file_name

        # play audio after recording
        self.play_audio()

    def play_audio(self):
        print("todo")

    # def cleanup(self):
    # if self.rpi:
    # GPIO.cleanup()


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
