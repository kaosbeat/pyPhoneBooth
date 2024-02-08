from whisper_cpp_python import Whisper
from whisper_cpp_python.whisper_cpp import whisper_progress_callback

def callback(ctx, state, i, p):
    print(i)

model = Whisper('./whisper.cpp/models/ggml-tiny.en.bin')
model.params.progress_callback = whisper_progress_callback(callback)

print(model.transcribe('dream_en.wav'))
