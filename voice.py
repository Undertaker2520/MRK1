import asyncio
import os
import re
import wave
import struct
import math
import time
import threading
import pygame
import numpy as np
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import edge_tts

pygame.mixer.quit()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)

VOICE = "it-IT-GiuseppeNeural"
audio_lock = threading.Lock()

def clean_text_for_speech(text: str) -> str:
    """Rimuove la sintassi Markdown e caratteri speciali per evitare che vengano letti a voce."""
    if not text:
        return ""
    cleaned = re.sub(r'[\*\#\_\~\`\>]', '', text)
    cleaned = re.sub(r'\[.*?\]\(.*?\)', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def play_hud_sound(sound_type: str = "activate"):
    """Genera ed emette un segnale acustico olografico Sci-Fi."""
    filename = f"hud_{sound_type}.wav"
    
    if not os.path.exists(filename):
        sample_rate = 44100
        duration = 0.10
        n_samples = int(sample_rate * duration)
        
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            
            freq_start = 900 if sound_type == "activate" else 1300
            freq_end = 1500 if sound_type == "activate" else 800
            
            for i in range(n_samples):
                t = float(i) / sample_rate
                freq = freq_start + (freq_end - freq_start) * (t / duration)
                val = int(14000.0 * math.sin(2.0 * math.pi * freq * t) * (1.0 - t / duration))
                data = struct.pack('<h', val)
                wav_file.writeframesraw(data)

    try:
        sound = pygame.mixer.Sound(filename)
        sound.set_volume(0.2)
        sound.play()
    except Exception:
        pass

async def _genera_audio(testo: str, output_file: str):
    testo_pulito = clean_text_for_speech(testo)
    communicate = edge_tts.Communicate(testo_pulito, VOICE, rate="+20%")
    await communicate.save(output_file)

STATIC_CACHE_DIR = "audio_cache"
if not os.path.exists(STATIC_CACHE_DIR):
    os.makedirs(STATIC_CACHE_DIR, exist_ok=True)

import hashlib

def parla(testo: str, async_play: bool = True):
    """Sintetizza e riproduce l'audio. Se async_play è True, viene eseguito in un thread separato senza bloccare l'interfaccia.
    Utilizza un sistema di Caching locale per le frasi ricorrenti per azzerare la latenza TTS.
    """
    if not testo:
        return

    def _worker():
        with audio_lock:
            testo_clean = clean_text_for_speech(testo)
            hash_name = hashlib.md5(testo_clean.encode('utf-8')).hexdigest()
            cached_file = os.path.join(STATIC_CACHE_DIR, f"{hash_name}.mp3")
            
            is_temp = False
            file_to_play = cached_file

            if not os.path.exists(cached_file):
                file_to_play = f"temp_response_{threading.get_ident()}.mp3"
                is_temp = True
                try:
                    asyncio.run(_genera_audio(testo_clean, file_to_play))
                    if len(testo_clean) <= 100:
                        try:
                            import shutil
                            shutil.copy(file_to_play, cached_file)
                        except Exception:
                            pass
                except Exception as e:
                    print(f"[ERRORE TTS]: {e}")
                    return

            try:
                pygame.mixer.music.load(file_to_play)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(20)
                    
                pygame.mixer.music.unload()
                if is_temp and os.path.exists(file_to_play):
                    try:
                        os.remove(file_to_play)
                    except Exception:
                        pass
            except Exception as e:
                print(f"[ERRORE AUDIO PLAYBACK]: {e}")

    if async_play:
        threading.Thread(target=_worker, daemon=True).start()
    else:
        _worker()

def cattura_audio_dinamico(status_callback=None, timeout_seconds=None) -> str:
    """
    Cattura l'audio in tempo reale tramite VAD (Voice Activity Detection).
    Avvia la registrazione dinamica non appena rileva la voce e si interrompe automaticamente
    quando rileva silenzio (pausa) o il limite massimo di durata.
    """
    from config_manager import load_config
    cfg = load_config().get("voice", {})
    silence_duration_limit = cfg.get("silence_duration", 0.8)
    max_duration_limit = cfg.get("max_duration", 10.0)
    sensitivity_mult = cfg.get("vad_sensitivity", 2.2)
    language = cfg.get("language", "it-IT")

    samplerate = 16000
    block_duration_ms = 50
    block_size = int(samplerate * (block_duration_ms / 1000.0))

    ambient_rms = 150.0
    speech_frames = []
    
    is_speaking = False
    silence_start_time = None
    speech_start_time = None
    start_listen_time = time.time()
    
    temp_wav = "temp_input.wav"

    def process_block(indata):
        nonlocal ambient_rms, is_speaking, silence_start_time, speech_start_time
        
        samples = indata.flatten()
        if len(samples) == 0:
            return False
            
        rms = float(np.sqrt(np.mean(samples.astype(np.float32) ** 2)))
        threshold = max(250.0, ambient_rms * sensitivity_mult)

        if not is_speaking:
            # Calibrazione adattiva del rumore di fondo
            ambient_rms = 0.95 * ambient_rms + 0.05 * rms
            if rms > threshold:
                is_speaking = True
                speech_start_time = time.time()
                silence_start_time = None
                if status_callback:
                    status_callback("RECORDING")
                speech_frames.append(indata.copy())
        else:
            speech_frames.append(indata.copy())
            if rms < threshold:
                if silence_start_time is None:
                    silence_start_time = time.time()
                elif (time.time() - silence_start_time) >= silence_duration_limit:
                    return True
            else:
                silence_start_time = None
                
            if speech_start_time and (time.time() - speech_start_time) >= max_duration_limit:
                return True
                
        return False

    try:
        with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16', blocksize=block_size) as stream:
            while True:
                if timeout_seconds and (time.time() - start_listen_time) > timeout_seconds and not is_speaking:
                    return ""

                data, overflowed = stream.read(block_size)
                stop_requested = process_block(data)
                if stop_requested:
                    break

        if not speech_frames:
            return ""

        if status_callback:
            status_callback("RECOGNIZING")

        audio_concat = np.concatenate(speech_frames, axis=0)
        sf.write(temp_wav, audio_concat, samplerate)

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_wav) as source:
            audio_data = recognizer.record(source)
            testo = recognizer.recognize_google(audio_data, language=language)
            print(f"Tu (Vocale VAD): {testo}")

        if os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except Exception:
                pass

        return testo

    except sr.UnknownValueError:
        if os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except Exception:
                pass
        return ""
    except Exception as e:
        if os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except Exception:
                pass
        return ""

def ascolta(status_callback=None) -> str:
    """Ascolta tramite VAD dinamico senza blocchi fissi a tempo."""
    return cattura_audio_dinamico(status_callback=status_callback)

def ascolta_wake_word(status_callback=None) -> tuple[bool, str]:
    """
    Ascolta continuamente in modalità VAD.
    Quando rileva la voce, analizza il testo per identificare la Wake Word configurata (es. 'Galileo', 'Jarvis').
    Se la Wake Word è presente, riproduce il suono HUD ed estrae eventuale comando integrato.
    """
    testo = cattura_audio_dinamico(status_callback=status_callback)
    if not testo:
        return False, ""
        
    testo_lower = testo.lower().strip()
    from config_manager import load_config
    cfg = load_config().get("voice", {})
    wake_words = cfg.get("wake_words", ["galileo", "jarvis", "ehi galileo", "hey galileo", "ok galileo", "galilei"])

    for kw in wake_words:
        kw_lower = kw.lower().strip()
        if re.search(r'\b' + re.escape(kw_lower) + r'\b', testo_lower) or kw_lower in testo_lower:
            play_hud_sound("activate")
            parti = re.split(r'\b' + re.escape(kw_lower) + r'\b', testo_lower, maxsplit=1)
            if len(parti) < 2:
                parti = testo_lower.split(kw_lower, 1)
                
            comando_post_wake = parti[1].strip() if len(parti) > 1 else ""
            comando_post_wake = re.sub(r'^[,\.\s\-:]+', '', comando_post_wake)
            return True, comando_post_wake

    return False, ""