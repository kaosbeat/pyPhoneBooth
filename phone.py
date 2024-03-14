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


status = {
    "ready" : False,
    "phonehookstate"  : True
}


# Define a function to speak a long sentence in the background:


if len(sys.argv) != 4:
    print("Usage: python script.py name server options")
    sys.exit(1)

name = sys.argv[1]
server = sys.argv[2]
options = sys.argv[3]


def say(text, voice="en-gb-scotland+f2", pitch=80, speed=125):
    #-v "english_rp+f2", "en-scottish"
    #-p (pitch 0-99, 50 default)
    #-s <integer>  Speed in approximate words per minute. The default is 175
    p = subprocess.Popen(['espeak-ng', "-p", str(pitch) , "-v", voice , "-s", str(speed), text])
    return p


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
say("Hi, "+ sys.argv[1]  + "activated")

def sendStatus(ws, status, data):
    status  = {
        "type": "status",
        "status": status,
        "data" : data,
        "src": name
    }
    ws.send(json.dumps(status))

def sendCommand(ws, command, data):
    command  = {
        "type": "command",
        "command": command,
        "data" : data,
        "src": name
    }
    ws.send(json.dumps(command))





def transcribe_wav(wav_file):
    model = whisper.load_model("tiny.en")#"base")
    now = time.time()
    result = model.transcribe(wav_file)
    print(result["text"])
    print("calculation took :", time.time() - now , "sec" )
    return result["text"]



class AudioRecorder:
    global status
    def __init__(self, rpi_execution: bool = False):
        self.recording = None
        self.rpi = False
        self.samplerate = 44100
        self.block_size = 1024
        self.channels = 1
        self.duration = 10
        self.p = say("")
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
        global status
        status["phonehookstate"] = False
        sendStatus(ws, "hook", "off")
        print("Phone off Hook")
        if status["ready"]:
            self.p = say("   ")
            self.p.wait()
            self.p = say("Hi, Welcome to Data Driven Dreams")
            self.p.wait()
            sendCommand(ws, "show", {"text":"You have ten seconds to describe your dream in one sentence. Ready?", "textstate": "busy"})
            self.p = say("You have ten seconds to describe your dream in one sentence. Ready?" )  # 3 2 1 Go!")
            self.p.wait()
            sendCommand(ws, "show", {"text":"here is some inspiration", "textstate": "busy"})
            sendCommand(ws, "inspire", 3 )
            sendCommand(ws, "show", {"text":"Keep it short, and please speak English. One sentence", "textstate": "busy"})
            self.p = say("Keep it short, and please speak english. One sentence... Ready?" )  
            sendCommand(ws, "showbig", {"text":"READY?", "textstate": "busy"})
            self.p.wait()
            sendCommand(ws, "showbig", {"text":"3", "textstate": "alert"})
            self.p = say("3")
            self.p.wait()
            sendCommand(ws, "showbig", {"text":"2", "textstate": "alert"})
            self.p = say("2")
            self.p.wait()
            sendCommand(ws, "showbig", {"text":"1", "textstate": "alert"})
            self.p = say("1")
            self.p.wait()
            sendCommand(ws, "showbig", {"text":"REC", "textstate": "alert"})
            self.p = say("GO!")
            self.p.wait()
            print("starting recording")
            sendStatus(ws, "recording", True)
            # Start recording in a separate thread
            self.recording = True
            threading.Thread(target=self.record_audio).start()



    def stop_recording(self):
        sendStatus(ws, "hook", "on")
        status["phonehookstate"] = True
        self.recording = False
        # self.p.kill()
        print("Recording stopped")
        sendStatus(ws, "recording", False)
        self.gpio.switch_led(to_green=False)

    def record_audio(self):
        status["ready"] = False
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
                    sendCommand(ws, "showbig", {"text":"REC Done", "textstate": "busy"})
                    sendCommand(ws, "show", {"text":"converting to text", "textstate": "busy"})
                    

            # normalize the audio
            try:
                raw_sound = AudioSegment.from_file(file_name, "wav")
                normalized_sound = effects.normalize(raw_sound)
                normalized_sound.export(file_name, format="wav")
            except IndexError:
                status["ready"] = True
        except sd.PortAudioError as e:
            print("PA error {}".format(e))
            # try again, miserable portaudio library
            self.record_audio()
        if not status["ready"]:
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
    global phonehookstate
    event = json.loads(message)
    print(event)
    if event["type"] == "command" and event["dest"] == name:
        # print(event["text"]) 
        if event["command"] == "say":
            if event["data"]["style"] == "female":
                voice = "en-us-nyc"
            if event["data"]["style"] == "male":
                voice = "en-029"
            # engine.setProperty('rate', random.randint(80,120))
            say(event["data"]["text"],voice, 90 )
        if event["command"] == "stt":
            print("converting speech to text")
            inputtext = transcribe_wav(event["data"])
            sendStatus(ws, "sttdone", inputtext)
            p = say(inputtext)
            p.wait()
            sendCommand(ws, "show", {"text":"follow your dreams, go see the installation", "textstate": "busy"})
            p = say("please hang up the phone,   bye" , voice="en-gb", speed=110)  # 3 2 1 Go!")
            p.wait()
            sendCommand(ws, "show", {"text":"_"*40, "textstate": "info"})
            sendCommand(ws, "show", {"text":"Dear Visitor,", "textstate": "info"})
            sendCommand(ws, "show", {"text":"Welcome", "textstate": "boldinfo", "linefeed":False})
            sendCommand(ws, "show", {"text":"Data Driven Dreams", "textstate": "boldinfo"})
            sendCommand(ws, "show", {"text":"Here you can have an AI agent help you dive into your dreams", "textstate": "info"})
            sendCommand(ws, "show", {"text":"The Agent will help you as soon as you pick up the phone", "textstate": "info"})
            sendCommand(ws, "show", {"text":"Before you do, think of what you will say. You have 10 seconds", "textstate": "info"})
            sendCommand(ws, "show", {"text":"How would you tell your dream, in ", "textstate": "info"})
            sendCommand(ws, "show", {"text":"one sentence...", "textstate": "boldinfo"})
            sendCommand(ws, "show", {"text":"after that, you can see it being processed by the AI in the", "textstate": "info"})
            sendCommand(ws, "show", {"text":"Processing Tower", "textstate": "boldinfo"})

            sendCommand(ws, "show", {"text":"Now, Pick up...dream and explore it in this room", "textstate": "info"})

            status["ready"] = True
            

        if event["command"] == "enableInput":
            print("readsy to accept new input")
            status["ready"] = True
        if event["command"] == "disableInput":
            print("not readsy to accept new input")
    if event["type"] == "status" and event["dest"] == name:
        if event["status"] == "hook":
            if event["data"] == "off":
                phonehookstate = False # False is off hook
            if event["data"] == "on":
                phonehookstate = True # False is off hook
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
    status["ready"] = True


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
