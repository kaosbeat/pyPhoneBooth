import time
import pyaudio
import wave
import threading
import librosa
from detect_pi import is_raspberrypi
import os


class AudioRecorder:
    def __init__(self, rpi_execution: bool = False):
        self.recording = None
        self.rpi = False
        if rpi_execution:
            from gpio_class import gpio_class
            print("RPI execution")
            self.rpi = True
            self.gpio = gpio_class(callback_function=self.adapt_recording)
            print("GPIO initialised")
        else:
            print("running on reg pc")
            from pynput import keyboard
            listener = keyboard.Listener(
                on_press=self.start_recording_key,
                on_release=self.stop_recording_key)
            listener.start()
        # recording files
        self.frames = []

        self.latest_recording = ""
        # Audio parameters
        self.FORMAT = pyaudio.paInt24
        self.CHANNELS = 2
        self.RATE = 44100
        self.CHUNK = 1024

        # Audio stream
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.FORMAT,
                                      channels=self.CHANNELS,
                                      rate=self.RATE,
                                      input=True,
                                      frames_per_buffer=self.CHUNK)
        #                                      input_device_index=0)

        print("audio recorder initialized")

    def adapt_recording(self, channel):
        print("gpio callback triggered")
        time.sleep(0.1)  # time delay for false readings
        if GPIO.input(channel) == GPIO.LOW:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording_key(self, key):
        if key.char == 'r':
            self.start_recording()

    def stop_recording_key(self, key):
        if key.char == 'r':
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

        print(threading.active_count())

        self.frames.clear()
        print("ready to capture data")
        while self.recording:
            data = self.stream.read(self.CHUNK)
            print(data)
            self.frames.append(data)

        print("Finished recording")
        print(len(self.frames))
        wf = wave.open(file_name, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        self.latest_recording = file_name

        # play audio after recording
        self.play_audio()

    def play_audio(self):
        wf = wave.open(self.latest_recording, 'rb')

        stream = self.audio.open(format=self.audio.get_format_from_width(wf.getsampwidth()),
                                 channels=wf.getnchannels(),
                                 rate=wf.getframerate(),
                                 output=True)
        duration = librosa.get_duration(path=self.latest_recording)
        print("Playing audio {} for {}s".format(self.latest_recording, duration))

        data = wf.readframes(self.CHUNK)

        while data:
            stream.write(data)
            data = wf.readframes(self.CHUNK)

        print("Finished playing audio")

        stream.stop_stream()
        stream.close()

    def cleanup(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def check_devices(self):
        info = self.audio.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        for i in range(0, num_devices):
            if (self.audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print("Input Device id ", i, " - ", self.audio.get_device_info_by_host_api_device_index(0, i))


#        for i in range(self.audio.get_device_count()):
#           print(self.audio.get_device_info_by_index(i))

if __name__ == "__main__":
    try:
        import RPi.GPIO as GPIO
    except:
        print("no rpi?")

    audio_recorder = AudioRecorder(is_raspberrypi())
    # audio_recorder.check_devices()
    try:
        print("Waiting for button press...")
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        audio_recorder.cleanup()
