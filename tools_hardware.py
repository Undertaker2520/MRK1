import io
import datetime
import pyautogui
import psutil
import screen_brightness_control as sbc
from PIL import Image
from google import genai
from google.genai import types

def screen_shot(file_name: str = "screenshot_jarvis.png") -> str:
    """Scatta uno screenshot del desktop e lo salva su disco."""
    try:
        if not file_name.endswith('.png'):
            file_name += '.png'
        screenshot = pyautogui.screenshot()
        screenshot.save(file_name)
        return f"Screenshot salvato con successo come '{file_name}'."
    except Exception as e:
        return f"Errore nel salvataggio dello screenshot: {e}"

def analyze_screen(prompt_utente: str = "Cosa c'è sullo schermo?") -> str:
    """Cattura lo schermo ed effettua un'analisi visiva intelligente tramite IA multimodale.
    
    IMPORTANTE: Usa questo tool SOLO ED ESCLUSIVAMENTE quando l'utente ti chiede di 'guardare', 'analizzare', 'leggere' o 'osservare' lo schermo.
    
    Args:
        prompt_utente: La domanda specifica dell'utente relativa a ciò che vede a schermo.
    """
    try:
        # 1. Cattura dello schermo in RAM
        screenshot = pyautogui.screenshot()
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        # 2. Invocazione modello visivo Gemini 2.0 Flash
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                f"Sei GALILEO (J.A.R.V.I.S.). Analizza lo schermo e rispondi al Signore in massimo 2 frasi concise ed eleganti alla sua richiesta: {prompt_utente}"
            ]
        )
        return response.text or "Nessun elemento rilevante identificato sullo schermo, Signore."
        
    except Exception as e:
        err_msg = str(e)
        # Gestione pulita del rate-limit senza leggere stringhe JSON
        if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "Quota" in err_msg:
            return "Modulo visivo momentaneamente non disponibile per limite di quota Cloud, Signore."
        return "Impossibile completare l'analisi visiva dello schermo in questo momento, Signore."

def volume_control(action: str) -> str:
    """Controlla il volume del PC (MUTA, AUMENTA, ABBASSA)."""
    act = str(action).upper()
    if act in ["MUTA", "MUTE"]:
        pyautogui.press("volumemute")
        return "Volume mutato."
    elif act in ["AUMENTA", "UP", "AUMENTA VOLUME"]:
        pyautogui.press("volumeup", presses=5)
        return "Volume alzato."
    elif act in ["ABBASSA", "DOWN", "ABBASSA VOLUME"]:
        pyautogui.press("volumedown", presses=5)
        return "Volume abbassato."
    else:
        return f"Azione '{action}' non valida per il volume."

def brightness_control(value: int) -> str:
    """Imposta la luminosità dello schermo (0-100%)."""
    try:
        level = int(value)
        level = max(0, min(100, level))
        sbc.set_brightness(level)
        return f"Luminosità dello schermo impostata al {level}%."
    except Exception as e:
        return f"Impossibile regolare la luminosità: {e}"

def get_system_status() -> str:
    """Restituisce lo stato hardware attuale del PC: CPU, RAM e Batteria."""
    try:
        cpu_usage = psutil.cpu_percent(interval=0.3)
        ram = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        
        status_msg = f"Utilizzo CPU: {cpu_usage}%. RAM usata: {ram.percent}% ({round(ram.used / (1024**3), 1)}GB di {round(ram.total / (1024**3), 1)}GB)."
        if battery:
            stato_carica = "in carica" if battery.power_plugged else "a batteria"
            status_msg += f" Batteria al {battery.percent}% ({stato_carica})."
            
        return status_msg
    except Exception as e:
        return f"Impossibile recuperare lo stato di sistema: {e}"

def get_tactical_briefing() -> str:
    """Genera un briefing tattico di benvenuto con orario, data e stato della telemetria hardware del PC."""
    now = datetime.datetime.now()
    ora_str = now.strftime("%H:%M")
    
    try:
        cpu_usage = psutil.cpu_percent(interval=0.2)
        ram = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        
        briefing = f"Report operativo delle ore {ora_str}. CPU al {cpu_usage}%, Memoria RAM occupata al {ram.percent}%."
        if battery:
            briefing += f" Livello batteria: {battery.percent}%."
        return briefing
    except Exception as e:
        return f"Sistemi operativi attivi alle ore {ora_str}. Telemetria parziale: {e}"