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

        # Set up button event detection
        GPIO.add_event_detect(self.GPIO_BUTTON, GPIO.BOTH, callback=self.adapt_recording, bouncetime=300)

        #recording files
        self.latest_recording = ""

    def adapt_recording(self, channel):
        if GPIO.input(self.GPIO_BUTTON) == GPIO.HIGH:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.recording = True
        print("Recording started")
        GPIO.output(self.GPIO_RED_LED, GPIO.HIGH)
        GPIO.output(self.GPIO_GREEN_LED, GPIO.LOW)

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
#            print(data)
            frames.append(data)

        print("Finished recording")

        wf = wave.open(file_name, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        self.latest_recording = file_name
        
        #play audio after recording
        self.play_audio()
        
    def play_audio(self):
        wf = wave.open(self.latest_recording, 'rb')

        stream = self.audio.open(format=self.audio.get_format_from_width(wf.getsampwidth()),
                                 channels=wf.getnchannels(),
                                 rate=wf.getframerate(),
                                 output=True)

        print("Playing audio {}".format(self.latest_recording))

        data = wf.readframes(self.CHUNK)

        while data:
            stream.write(data)
            data = wf.readframes(self.CHUNK)

        print("Finished playing audio")

        stream.stop_stream()
        stream.close()


    def cleanup(self):
        GPIO.cleanup()
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        
    def check_devices(self):
        info = self.audio.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
                if (self.audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    print("Input Device id ", i, " - ", self.audio.get_device_info_by_host_api_device_index(0, i))
        
#        for i in range(self.audio.get_device_count()):
 #           print(self.audio.get_device_info_by_index(i))

if __name__ == "__main__":
    audio_recorder = AudioRecorder()
    audio_recorder.check_devices()
    try:
        print("Waiting for button press...")
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        audio_recorder.cleanup()
