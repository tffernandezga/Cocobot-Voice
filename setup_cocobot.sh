#!/bin/bash

echo "📦 Updating the system..."
sudo apt-get update && sudo apt-get upgrade -y

echo "🐍 Installing Python 3 and related tools..."
sudo apt-get install -y python3 python3-pip python3-dev

echo "🔧 Installing system dependencies..."
sudo apt-get install -y libusb-1.0-0-dev libasound2-dev libudev-dev alsa-utils ffmpeg mpg123 git

echo "📦 Installing Python libraries..."
pip3 install --upgrade pip
pip3 install openai pydub pvporcupine pyusb pyaudio numpy pyttsx3 gTTS

echo "📁 Cloning ReSpeaker firmware tools..."
git clone https://github.com/respeaker/usb_4_mic_array.git
cd usb_4_mic_array

echo "⬇️ Installing firmware (make sure the ReSpeaker is connected)..."
sudo python3 dfu.py --download 6_channels_firmware.bin

cd ..

echo "📂 Creating required directories in /home..."
mkdir -p /home/models
mkdir -p /home/audios
mkdir -p /home/scripts

echo "✅ Installation complete. You can run 'lsusb' to verify that the ReSpeaker was correctly detected."
