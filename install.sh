python -m venv env --system-site-packages
source env/bin/activate
sudo apt install python3-pyaudio python3-soundfile
pip install -r requirements.txt
git clone https://github.com/raspberrypi/Pi-Codec.git codec_zero
