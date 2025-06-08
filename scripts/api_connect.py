#Tomás Feernández Garrido, Universidad Pontificia de Salamanca 2025
import openai
import os
import time
import openai
import os
import subprocess
from openai import OpenAI



#Inicializa la API con tu clave usando el nuevo cliente
client = OpenAI(api_key="ACCESS KEY")

mensaje_sistema = {
    "role": "system",
    "content": (
        "Eres Cocobot, un robot asistente diseñado para interactuar con humanos mediante voz. "
        "Respondes de forma clara, educada y concisa. "
        "Si te preguntan quién eres, debes responder: 'Soy Cocobot, un robot diseñado para interactuat con humanos desarrollado por la Universidad Pontificia de Salamanca'. "
        "Si te preguntan por tus características técnicas, debes explicar que utilizas una arquitectura híbrida "
        "con procesamiento local (como detección de palabra clave y actividad de voz) y servicios en la nube "
        "para tareas como reconocimiento de voz, procesamiento del lenguaje y síntesis de voz. "
        "Eres eficiente, optimizas recursos y evitas hacer llamadas innecesarias a la nube."
        "Si alguna consulta no te queda clara o no tiene sentido, pide que te la repitan."
    )
}


#Función para transcribir de voz a texto mediante la API
def transcribe_audio(audio_file_path):
    try:
        with open(audio_file_path, 'rb') as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="es"
            )
        transcription = response.text
        return transcription
    except Exception as e:
        print(f"Error al transcribir el audio: {e}")
        return None

#Función para generar una respuesta mediante la API
def get_chatgpt_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[mensaje_sistema, {"role": "user", "content": prompt}],
            max_tokens=150
        )
        answer = response.choices[0].message.content.strip()
        return answer
    except Exception as e:
        print(f"Error al obtener respuesta de ChatGPT: {e}")
        return None

#Función que convierte la respuesta en audio mediante la API
def convert_text_to_speech(text, voice="onyx"):
    try:
        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text
        )
        audio_file_path = '/tmp/temp_audio.mp3'
        response.stream_to_file(audio_file_path)
        return audio_file_path
    except Exception as e:
        print(f"Error al convertir texto a voz: {e}")
        return None


