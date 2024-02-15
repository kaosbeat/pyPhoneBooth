# pyPhoneBooth

Can we use an old phone to capture speech and send it to a STT service? Can we use the same phone to receive text do TTS sound to the horn

Yes we can!

# hardware

## old phone 

![image](https://github.com/kaosbeat/pyPhoneBooth/assets/204628/91c8c5cb-8907-4e97-a9a6-d5bbaccf0e94)

I used this one

## microcoputer
RPi + audio codec


# software

## STT models

[huggingface overview](https://huggingface.co/tasks/automatic-speech-recognition)  

[RPi4 realtime STT](https://www.youtube.com/watch?v=caaKhWcfcCY)  

## Whisper SOTA

[RPi4 realtime STT](https://www.youtube.com/watch?v=caaKhWcfcCY)
```
button off hook
  |
  v
play instruction message
  |
  v
record audio --> convert to correct samplerate
  |
  v 
send to STT service (over IP)
```

# physicall connections

## microphone input

When using electret microphone, I'm doubting if we need to have some gain on the electret side.

Audio comes in via MIC2_N, when using electret. MIC2_P when using onboard MEMS.

You need to use a coax cable coming from the electret to the stereo minijack (3.5mm)
The tip is hot, the ring is cold, sleeve loose/cold.

## button

When wiring the phone button to GPIO 27 (same as button on IQAudio), I get lot's of incorrect readings.

I've changed the phone button from GPIO 17 to GND, with internal pullup. This way, when the phone is **on** the hook, we get a positive reading on the GPIO (no shortcut to GND). When the phone is **off** the hook, we get a shortcut to GND and thus a 0 reading on the GPIO.

Even with this adaption, I get some bad readings. 

**TODO** photo from internal connections of the phone & the IQAUDIO board **TODO**