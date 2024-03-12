python -m venv env --system-site-packages
source env/bin/activate
sudo apt install python3-pyaudio python3-soundfile
pip install -r requirements.txt
git clone https://github.com/raspberrypi/Pi-Codec.git codec_zero

echo "fixing lgpio by copying the main lgpio lib to the env"
cd env/lib/python3.11/site-packages
rm lgpio.py
rm -rf lgpio*
cp /usr/lib/python3/dist-packages/lgpio.py .
cp -r /usr/lib/python3/dist-packages/lgpio-0.2.2.0.egg-info/ .
cd ../../../../
