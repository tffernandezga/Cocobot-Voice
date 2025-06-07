#Tomás Feernández Garrido, Universidad Pontificia de Salamanca 2025
import time
import os
import random
import threading
import queue
import sys
import numpy as np
import wave
import openai
import shutil
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from datetime import datetime
from mic_detection import initialize_respeaker, detect_wake_word, detect_voice
from audio_capture import initialize_audio_stream, process_audio_data
from api_connect import get_chatgpt_response, convert_text_to_speech, transcribe_audio

AUDIO_ONYX_DIR = "/home/tomas/cocobot/audios/audios_onyx"
onyx_audio_files = [os.path.join(AUDIO_ONYX_DIR, f) for f in os.listdir(AUDIO_ONYX_DIR) if f.endswith('.wav')]

#Función para reproducir la frase de saludo
def play_random_onyx_audio():
    audio_to_play = random.choice(onyx_audio_files)
    os.system(f"aplay '{audio_to_play}'")
if len(sys.argv) != 2:
    sys.exit(1)

#Función que filtra los audios vacíos
#Considera como válidos solo los segmentos que superen el valor -35dBFS
def contiene_voz(ruta_audio, min_duracion_ms=300, silence_thresh=-35):
    audio = AudioSegment.from_file(ruta_audio, format="wav")
    no_silencios = detect_nonsilent(audio, min_silence_len=200, silence_thresh=silence_thresh)
    segmentos_validos = [
        (inicio, fin) for inicio, fin in no_silencios if (fin - inicio) >= min_duracion_ms
    ]
    
    return len(segmentos_validos) > 0

try:
    max_silencios = int(sys.argv[1])
except ValueError:
    print("Inserte el numero de silencios")
    sys.exit(1)

#Función principal para orquestar el flujo
def main():

    #Inicializar el dispositivo ReSpeaker
    mic_tuning = initialize_respeaker()

    #Inicializar PyAudio para capturar audio
    p, stream = initialize_audio_stream()

    #Cola para manejar los frames de audio
    frame_queue = queue.Queue(maxsize=10)

    #Variable de control para finalizar los hilos
    exit_flag = False
    is_waiting_for_api_response = False

    #Iniciar el hilo para procesar audio
    def process_audio_thread():
        while not exit_flag:
            process_audio_data(stream, frame_queue)
            time.sleep(0.05)

    audio_thread = threading.Thread(target=process_audio_thread)
    audio_thread.start()

    try:
        while not exit_flag:
            if is_waiting_for_api_response:
                print("🔒 El sistema está esperando la respuesta de la API. No se puede grabar.")
                time.sleep(1)  #Esperamos un segundo antes de volver a comprobar
                continue

            voice_detected = detect_voice(mic_tuning)

            if voice_detected == 1:
                print("🔊 Voz detectada, comenzando a grabar...")

                #Grabar hasta que se detecten 9 silencios consecutivos
                frames = []
                short_frames = []
                start_time = time.time()

                #Leer continuamente para detectar "Cocobot" al principio
                while time.time() - start_time < 2:
                    if not frame_queue.empty():
                        frame = frame_queue.get()
                        short_frames.append(frame)
                    time.sleep(0.05)

                short_pcm = np.frombuffer(b''.join(short_frames), dtype=np.int16)

                #Detectar la palabra clave "Cocobot", dividiendo el audio en bloques de 512 frames para Porcupine
                keyword_index = -1
                for i in range(0, len(short_pcm), 512):
                    frame = short_pcm[i:i + 512]
                    if len(frame) < 512:
                        break
                    keyword_index = detect_wake_word(frame)
                    if keyword_index >= 0:
                        print("✅ Wake word detectada al principio: Cocobot")
                        play_random_onyx_audio()
                        time.sleep(0.5)
                        break

                if keyword_index < 0:
                    print("❌ No se detectó la palabra clave al principio. Ignorando grabación.")
                    continue
             
                

                #Si detectamos "Cocobot", grabamos el audio completo
                print("🔊 Detectamos 'Cocobot' al principio. Grabando audio completo...")
                frames = []
                silence_count = 0  #Contador de silencios consecutivos
                start_time = time.time()

                max_duration = 20  #Duración máxima de grabación en segundos
                start_recording_time = time.time()

                while True:  #Continuar grabando mientras se detecte voz
                    if not frame_queue.empty():
                        frame = frame_queue.get()
                        frames.append(frame)

                    #Revisar si se detectan los silencios máximos consecutivos
                    if detect_voice(mic_tuning) == 0:
                        silence_count += 1
                    else:
                        silence_count = 0  #Restablecer el contador si se detecta voz
                        
                    #Si se detectaron loa silencios consecutivos máximos se para la grabación
                    if silence_count >= max_silencios:  
                        print("🛑 20 silencios consecutivos detectados. Deteniendo la grabación...")
                        break
                        
                    #Si la grabación dura más de 20 segundos se para
                    if time.time() - start_recording_time >= max_duration: 
                        print("⏱️ Tiempo máximo de grabación alcanzado. Deteniendo...")
                        break

                    time.sleep(0.05)

                timestamp = time.strftime("%Y%m%d-%H%M%S")
                wave_output_path = f"/tmp/{timestamp}_output.wav"
                wf = wave.open(wave_output_path, 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(p.get_sample_size(p.get_format_from_width(2)))
                wf.setframerate(16000)
                wf.writeframes(b''.join(frames))
                wf.close()
                
                #Comprobams que el audio grabado es válido (no está vacío) antes de mandarlo a la API
                if contiene_voz(wave_output_path):
                    print("🎶 El audio se ha guardado con éxito.")
                    transcription = transcribe_audio(wave_output_path)
                else:
                    print("Audio vacío detectado. No se enviará a Whisper.")
                    continue
                os.remove(wave_output_path)

                #Obtener la respuesta de la API de ChatGPT
                is_waiting_for_api_response = True
                api_response = get_chatgpt_response(transcription)
                
               

                #Convertir la respuesta a voz usando OpenAI TTS (voz masculina en español)
                #Reproducir el audio
                #Restablecer para volver a grabar
                audio_file_path = convert_text_to_speech(api_response, voice="onyx")
                os.system(f"mpg123 {audio_file_path}")  
                is_waiting_for_api_response = False  

            

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("🔴 Finalizando el programa por interrupción de teclado...")

    finally:
        # Limpiar y cerrar los hilos y recursos
        exit_flag = True  
        audio_thread.join() 
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Todos los recursos han sido liberados correctamente.")

# Iniciar el flujo principal
if __name__ == "__main__":
    main()


