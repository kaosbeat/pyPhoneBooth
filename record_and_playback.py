import RPi.GPIO as GPIO
import time
import pyaudio
import wave
import threading

class AudioRecorder:
    def __init__(self):
        # Define GPIO pins
        self.GPIO_BUTTON = 27
        self.GPIO_RED_LED = 24
        self.GPIO_GREEN_LED = 23

        # Set up GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GPIO_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.GPIO_RED_LED, GPIO.OUT)
        GPIO.setup(self.GPIO_GREEN_LED, GPIO.OUT)

        # Audio parameters
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024

        # Audio stream
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.FORMAT,
                                      channels=self.CHANNELS,
                                      rate=self.RATE,
                                      input=True,
                                      frames_per_buffer=self.CHUNK)

        # Set up button event detection
        GPIO.add_event_detect(self.GPIO_BUTTON, GPIO.BOTH, callback=self.adapt_recording, bouncetime=300)

    def adapt_recording(self, channel):
        if GPIO.input(self.GPIO_BUTTON) == GPIO.HIGH:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.recording = True
        print("Recording started")
        GPIO.output(self.GPIO_RED_LED, GPIO.HIGH)
        # Start recording in a separate thread
        threading.Thread(target=self.record_audio).start()

    def stop_recording(self):
        self.recording = False
        print("Recording stopped")
        GPIO.output(self.GPIO_RED_LED, GPIO.LOW)
        GPIO.output(self.GPIO_GREEN_LED, GPIO.HIGH)

    def record_audio(self):
        # Generate filename with timestamp
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        file_name = f"output_{timestamp}.wav"

        frames = []

        while self.recording:
            data = self.stream.read(self.CHUNK)
            frames.append(data)

        print("Finished recording")

        wf = wave.open(file_name, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

    def cleanup(self):
        GPIO.cleanup()
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

if __name__ == "__main__":
    audio_recorder = AudioRecorder()
    
    try:
        print("Waiting for button press...")
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        audio_recorder.cleanup()
