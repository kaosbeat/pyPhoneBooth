#!/bin/bash

# Define the file path
file="/boot/config.txt"

# Check if the file exists
if [ -f "$file" ]; then
    # Search for the line containing 'dtparam=audio=on' and prepend '#' to it
    sed -i '/dtparam=audio=on/s/^/#/' "$file"
    echo "Commented out 'dtparam=audio=on' in $file"
else
    echo "Error: File $file not found."
fi
