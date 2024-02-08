#!/bin/bash

# adapt boot config so that default audio is disabled
# Define the file path
file="/boot/firmware/config.txt"

# Check if the file exists
if [ -f "$file" ]; then
    # Search for the line containing 'dtparam=audio=on' and prepend '#' to it
    sed -i '/dtparam=audio=on/s/^/#/' "$file"
    echo "Commented out 'dtparam=audio=on' in $file"
else
    echo "Error: File $file not found."
fi

# load the alsoconfig file https://github.com/raspberrypi/Pi-Codec
# Define the line to be added
line="sudo alsactl restore -f codec_zero/Codec_Zero_OnboardMIC_record_and_SPK_playback.state"

# Define the file path
file2="/etc/rc.local"

# Check if the file exists
if [ -f "$file2" ]; then
    # Append the line to the file
    sudo sed -i "\$i$line" "$file2"
    echo "Line added to $file2"
else
    echo "Error: File $file2 not found."
fi
