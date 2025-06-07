# Cocobot Installation Manual (ReSpeaker Mic Array v2.0)
**Note:** Cocobot is specifically configured to work with the ReSpeaker Mic Array v2.0.  
If you wish to use a different microphone device, you will need to manually update the audio input configuration
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

## 8. Configure ReSpeaker Device Index

Follow these steps to identify the ReSpeaker Mic Array input device index:

### Step 1: Install PyAudio (if not already)

```bash
sudo pip install pyaudio
```

### Step 2: Create the script to get device index

```bash
cd ~
nano get_index.py
```

Paste the following code into `get_index.py`:

```python
import pyaudio

p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

for i in range(0, numdevices):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
```

### Step 3: Save and close the file

Press `Ctrl + X`, then `Y` to save and exit.

### Step 4: Run the script

```bash
sudo python get_index.py
```

Expected output:

```
Input Device id  2  -  ReSpeaker 4 Mic Array (UAC1.0): USB Audio (hw:1,0)
```

### Step 5: Use the correct index in your code

Update your script to set `RESPEAKER_INDEX` based on the detected ID:

```python
import pyaudio
import wave

RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 6  # 1 for 1_channel_firmware.bin or 6 for 6_channels_firmware.bin
RESPEAKER_WIDTH = 2
RESPEAKER_INDEX = 2  # Use the index number you got from get_index.py
```

You can now run your recording script to test audio capture.

## 9. Running Cocobot

To start Cocobot, use the following command:

```bash
python3 cocobotVoice.py {number_of_silences}
```

Replace `{number_of_silences}` with the number of consecutive silence detections before stopping the recording (e.g., `20`).

