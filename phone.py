import sys
import asyncio
import websocket
import _thread
import time
import rel
import json
# import pyttsx4
import time
import random
import queue
import sys
import time
import os
import sounddevice as sd
import soundfile as sf
import wave
import threading
import librosa
from detect_pi import is_raspberrypi, raspberrypi_version
import numpy  # Make sure NumPy is loaded before it is used in the callback

assert numpy  # avoid "imported but unused" message (W0611)
from pydub import AudioSegment, effects
from config import mainserver
import subprocess
import whisper
import time

# Define a function to speak a long sentence in the background:


if len(sys.argv) != 4:
    print("Usage: python script.py name server options")
    sys.exit(1)

name = sys.argv[1]
server = sys.argv[2]
options = sys.argv[3]




def say(text, voice="en-gb-scotland+f2", pitch=50):
    #-v "english_rp+f2", "en-scottish"
    #-p (pitch 0-99, 50 default)
    #-s <integer>  Speed in approximate words per minute. The default is 175
    subprocess.Popen(['espeak-ng', "-p", "80" , "-v", voice , text])

# ESPEAK-NG voices
# 5  en-029          --/M      English_(Caribbean) gmw/en-029           (en 10)
#  2  en-gb           --/M      English_(Great_Britain) gmw/en               (en 2)
#  5  en-gb-scotland  --/M      English_(Scotland) gmw/en-GB-scotland   (en 4)
#  5  en-gb-x-gbclan  --/M      English_(Lancaster) gmw/en-GB-x-gbclan   (en-gb 3)(en 5)
#  5  en-gb-x-gbcwmd  --/M      English_(West_Midlands) gmw/en-GB-x-gbcwmd   (en-gb 9)(en 9)
#  5  en-gb-x-rp      --/M      English_(Received_Pronunciation) gmw/en-GB-x-rp       (en-gb 4)(en 5)
#  2  en-us           --/M      English_(America)  gmw/en-US            (en 3)
#  5  en-us-nyc       --/M      English_(America,_New_York_City) gmw/en-US-nyc  

## add +f2 for female voice

def sendStatus(ws, status, data):
    status  = {
        "type": "status",
        "status": status,
        "data" : data,
        "src": name
    }
    ws.send(json.dumps(status))


def transcribe_wav(wav_file):
    model = whisper.load_model("tiny.en")#"base")
    now = time.time()
    result = model.transcribe(wav_file)
    print(result["text"])
    print("calculation took :", time.time() - now , "sec" )
    return result["text"]

say("Hi, "+ sys.argv[1]  + "activated")

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
        sendStatus(ws, "hook", "off")
        print("Phone off Hook")
        say("please speak your dream loud and clear after this message. Ready? 3 2 1 Go!")
        print("starting recording")
        sendStatus(ws, "recording", True)
        # Start recording in a separate thread
        self.recording = True
        threading.Thread(target=self.record_audio).start()


    def stop_recording(self):
        self.recording = False
        print("Recording stopped")
        sendStatus(ws, "recording", False)
        self.gpio.switch_led(to_green=False)
        sendStatus(ws, "hook", "on")

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
        sendStatus(ws, "recording", False)
        sendStatus(ws, "recording_done", file_name)
        

    def play_audio(self, audio_file):
        try:
            data, fs = sf.read(audio_file)
            sd.play(data, fs)
            sd.wait()
        except sd.PortAudioError as e:
            print("PA error {}".format(e))
            # try again, miserable portaudio library
            self.play_audio(audio_file)


def on_message(ws, message):
    event = json.loads(message)
    print(event)
    if event["type"] == "command" and event["dest"] == name:
        # print(event["text"]) 
        if event["command"] == "say":
            if event["data"]["style"] == "female":
                voice = "english_rp+f2"
            if event["data"]["style"] == "male":
                voice = "en-scottish"
            # engine.setProperty('rate', random.randint(80,120))
            say(event["data"]["text"],voice, 90 )

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")
    say("speaker "+ name  + "disconnected ")


def on_open(ws):
    print("Opened connection")
    # ws.send("Hello, World")
    initstatus  = {
            "type": "status",
            "status": "init",
            "src": name
        }
    ws.send(json.dumps(initstatus))
    say("speaker: "+ name + ", connected to " + mainserver)


if __name__ == "__main__":
    try:
        import RPi.GPIO as GPIO
    except:
        print("no rpi?")

    # websocket.enableTrace(True)
    audio_recorder = AudioRecorder(is_raspberrypi())
    ws = websocket.WebSocketApp(mainserver,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()




    # audio_recorder.check_devices()
    print("Waiting for button press...")
    while True:
        time.sleep(0.1)
