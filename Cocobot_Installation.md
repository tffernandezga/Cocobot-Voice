# Cocobot Installation and User Manual (ReSpeaker Mic Array v2.0)

## 1. System Preparation

Make sure your Linux system is up to date and has internet access:

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

## 2. Connect the ReSpeaker Mic Array v2.0

Plug the ReSpeaker Mic Array v2.0 into a USB port.

Check that it is detected:

```bash
lsusb
```

Expected output:

```
Bus 001 Device 004: ID 2886:0018
```

## 3. Install Required System Packages

Install Python 3 and system-level dependencies:

```bash
sudo apt-get install -y python3 python3-pip python3-dev \
    libusb-1.0-0-dev libasound2-dev libudev-dev \
    alsa-utils ffmpeg mpg123 git
```

## 4. Install Python Libraries

Install all required Python libraries using pip:

```bash
pip3 install --upgrade pip
pip3 install openai pydub pvporcupine pyusb pyaudio numpy pyttsx3 gTTS
```

## 5. Clone and Install ReSpeaker Firmware

Clone the firmware tools and install the 6-channel firmware:

```bash
git clone https://github.com/respeaker/usb_4_mic_array.git
cd usb_4_mic_array
sudo python3 dfu.py --download 6_channels_firmware.bin
cd ..
```

## 6. Create Project Directories

Create necessary folders:

```bash
mkdir -p /home/models
mkdir -p /home/audios
mkdir -p /home/scripts
```

## 7. Setup Udev Rule for ReSpeaker (No sudo required)

To access ReSpeaker without root:

```bash
sudo nano /etc/udev/rules.d/99-respeaker.rules
```

Add the following line:

```bash
SUBSYSTEM=="usb", ATTR{idVendor}=="2886", ATTR{idProduct}=="0018", MODE="0666"
```

Apply the rule:

```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```

Add your user to the `plugdev` group:

```bash
sudo usermod -aG plugdev $USER
```

Then, reboot or reconnect the ReSpeaker.

## 8. Final Step

Reboot your system or replug the ReSpeaker and verify:

```bash
lsusb
```

You’re ready to run Cocobot!

## 9. Running Cocobot

To start Cocobot, use the following command:

```bash
python3 cocobotVoice.py {number_of_silences}
```

Replace `{number_of_silences}` with the number of consecutive silence detections you want before stopping the recording (e.g., `20`).
