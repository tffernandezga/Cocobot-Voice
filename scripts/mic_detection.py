#Tomás Feernández Garrido, Universidad Pontificia de Salamanca 2025
import usb.core
import time
from tuning import Tuning
import pvporcupine

#Configuración de la captación en 360º usando los 4 micrófonos
access_key = "ACCESS KEY"
keyword_file_path = "/home/user/cocobot/models/Coco-bot_es_linux_v3_0_0.ppn" #Ruta al archivo de la palabra clave
model_path = "/home/user/cocobot/models/porcupine_params_es.pv" #Ruta al modelo en español

#Configurar Porcupine para detectar la wake word "Cocobot"
porcupine = pvporcupine.create(
    access_key=access_key,
    keyword_paths=[keyword_file_path],  
    model_path=model_path  
)

#Función para inicializar el dispositivo ReSpeaker
def initialize_respeaker():
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
    if dev:
        mic_tuning = Tuning(dev)  # Crear objeto Tuning para controlar el dispositivo
        print("Dispositivo encontrado.")
        return mic_tuning
    else:
        print("No se encontró el dispositivo ReSpeaker.")
        exit()

#Función para detectar la palabra clave "Cocobot"
def detect_wake_word(pcm):
    return porcupine.process(pcm)

#Función para detectar si hay voz usando el dispositivo ReSpeaker
def detect_voice(mic_tuning):
    return mic_tuning.is_voice()

