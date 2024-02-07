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
<<<<<<< HEAD

## STT models

[huggingface overview](https://huggingface.co/tasks/automatic-speech-recognition)

[RPi4 realtime STT](https://www.youtube.com/watch?v=caaKhWcfcCY)
=======
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
>>>>>>> 0fc3f8ef2dfc368f2240a73d3e08873f61fd491b
