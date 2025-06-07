#Tomás Feernández Garrido, Universidad Pontificia de Salamanca 2025
import pyaudio
import numpy as np
import time
import queue
import pyttsx3
from gtts import gTTS
import os
import subprocess

#Parámetros de grabación
RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 6 
RESPEAKER_WIDTH = 2
CHUNK = 1024  

#Función para inicializar PyAudio y capturar el stream de audio
def initialize_audio_stream(respeaker_index=5):
    p = pyaudio.PyAudio()
    stream = p.open(
        rate=RESPEAKER_RATE,
        format=p.get_format_from_width(RESPEAKER_WIDTH),
        channels=RESPEAKER_CHANNELS,
        input=True,
        input_device_index=respeaker_index,
        frames_per_buffer=CHUNK
    )
    print("🎧 Escuchando continuamente...")
    return p, stream

#Función para procesar los datos de audio
#Extraemos los datos del canal 0 de los 6 canales
#Poner los datos en la cola de forma segura
def process_audio_data(stream, frame_queue, chunk_size=CHUNK):
    data = stream.read(chunk_size)  #Leer datos del stream
    a = np.frombuffer(data, dtype=np.int16)[0::6] 
    if not frame_queue.full():
        frame_queue.put(a.tobytes()) 



