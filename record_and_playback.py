import RPi.GPIO as GPIO
import time
import pyaudio
import wave


# Define GPIO pins
GPIO_BUTTON = 27
GPIO_RED_LED = 24
GPIO_GREEN_LED = 23

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_RED_LED, GPIO.OUT)
GPIO.setup(GPIO_GREEN_LED, GPIO.OUT)

# Audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

# Define callback function for button press
def button_callback(channel):
    print("Button pressed")
    GPIO.output(GPIO_RED_LED, GPIO.HIGH)
    record_audio()
    GPIO.output(GPIO_RED_LED, GPIO.LOW)
    GPIO.output(GPIO_GREEN_LED, GPIO.HIGH)
    play_audio()

# Set up button event detection
GPIO.add_event_detect(GPIO_BUTTON, GPIO.FALLING, callback=button_callback, bouncetime=300)

# Record audio function
def record_audio():
    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    print("Recording...")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# Playback audio function
def play_audio():
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'rb')

    audio = pyaudio.PyAudio()

    stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

    print("Playing audio...")

    data = wf.readframes(CHUNK)

    while data:
        stream.write(data)
        data = wf.readframes(CHUNK)

    print("Finished playing audio")

    stream.stop_stream()
    stream.close()
    audio.terminate()


try:
    print("Waiting for button press...")
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()
