import whisper
import time
import argparse

def transcribe_wav(wav_file):
		now = time.time()

		model = whisper.load_model("tiny.en")#"base")
		result = model.transcribe(wav_file)
		print(result["text"])
		print("calculation took :", time.time() - now , "sec" )

def transcribe_nl(wav_file):

		# now detecting language

		model = whisper.load_model("base")

		# load audio and pad/trim it to fit 30 seconds
		audio = whisper.load_audio(wav_file)
		#audio = whisper.load_audio("dream_nl2.wav")

		audio = whisper.pad_or_trim(audio)

		# make log-Mel spectrogram and move to the same device as the model
		mel = whisper.log_mel_spectrogram(audio).to(model.device)

		# detect the spoken language
		_, probs = model.detect_language(mel)
		print(f"Detected language: {max(probs, key=probs.get)}")

		# decode the audio
		options = whisper.DecodingOptions()
		result = whisper.decode(model, mel, options)

		# print the recognized text
		print(result.text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a WAV file and display its properties.")
    parser.add_argument("wav_file", nargs="?", default="dream_en.wav", help="Path to the WAV file (default: dream_en.wav)")

    args = parser.parse_args()
    wav_file = args.wav_file
    
    transcribe_wav(wav_file)
#    transcribe_nl(wav_file)
