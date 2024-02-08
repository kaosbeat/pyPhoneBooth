from pywhispercpp.model import Model

model = Model('base.en', n_threads=3)
segments = model.transcribe('dream_en.wav', speed_up=True)
for segment in segments:
    print(segment.text)