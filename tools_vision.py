import io
import time
import pyautogui
from PIL import Image
from google import genai
from google.genai import types

def detect_screen_errors() -> str:
    """Ispeziona lo schermo alla ricerca di errori di compilazione, eccezioni di codice nell'IDE, stack traces o errori di terminale.
    
    Usa questo tool quando l'utente ti chiede 'che errore c'è a schermo?', 'perché il codice non compila?', 'leggi l'eccezione nell'IDE' o 'trova l'errore'.
    """
    try:
        screenshot = pyautogui.screenshot()
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        client = genai.Client()
        prompt = (
            "Esamina con massima precisione questo screenshot di sviluppo.\n"
            "1. Identifica se è presente un errore di codice, eccezione o warning nell'IDE/terminale.\n"
            "2. Estrai il testo esatto dell'errore e il file/riga coinvolti se visibili.\n"
            "3. Spiega brevemente la causa dell'errore ed una possibile soluzione.\n"
            "Sii sintetico ed elegante nel formato Stark, senza usare formattazione Markdown (niente asterischi)."
        )
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                prompt
            ]
        )
        return response.text or "Nessun errore evidente rilevato a schermo."
        
    except Exception as e:
        err_str = str(e)
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
            return "Modulo visivo momentaneamente in quota cloud limitata."
        return f"Impossibile completare l'ispezione degli errori a schermo: {e}"

def click_ui_element(element_name: str) -> str:
    """Trova visivamente un elemento dell'interfaccia utente (pulsante, icona, scheda o testo) ed esegue un click con il mouse su di esso.
    
    Args:
        element_name: Descrizione dell'elemento da cliccare (es. 'pulsante Run', 'pulsante Salva', 'scheda Terminale', 'icona Cerca').
    """
    try:
        width, height = pyautogui.size()
        screenshot = pyautogui.screenshot()
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        client = genai.Client()
        prompt = (
            f"Stiamo cercando l'elemento dell'interfaccia utente: '{element_name}'.\n"
            f"La risoluzione totale dello schermo è {width}x{height}.\n"
            "Stima le coordinate (X, Y) in pixel del centro esatto dell'elemento richiesto.\n"
            "Rispondi SOLTANTO con due numeri interi separati da virgola, ad esempio: 850, 420."
        )
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                prompt
            ]
        )
        
        raw_coords = response.text.strip()
        parts = [p.strip() for p in raw_coords.replace('(', '').replace(')', '').split(',')]
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            x = int(parts[0])
            y = int(parts[1])
            x = max(0, min(width - 1, x))
            y = max(0, min(height - 1, y))
            
            pyautogui.moveTo(x, y, duration=0.4)
            pyautogui.click(x, y)
            return f"Click eseguito con successo sull'elemento '{element_name}' alle coordinate ({x}, {y})."
        else:
            return f"Impossibile identificare le coordinate esatte per '{element_name}' a schermo ({raw_coords})."
            
    except Exception as e:
        return f"Errore nell'esecuzione del click sull'elemento '{element_name}': {e}"

def type_or_press_keys(keys_or_text: str, is_shortcut: bool = False) -> str:
    """Scrive del testo oppure esegue una combinazione di tasti sulla tastiera.
    
    Args:
        keys_or_text: Il testo da digitare oppure la scorciatoia (es. 'ctrl+s', 'alt+tab', 'enter', 'ctrl+shift+f').
        is_shortcut: True se si tratta di una combinazione di tasti, False per digitare testo semplice.
    """
    try:
        if is_shortcut or "+" in keys_or_text or keys_or_text.lower() in ["enter", "tab", "esc", "space"]:
            tasti = [k.strip().lower() for k in keys_or_text.split("+")]
            pyautogui.hotkey(*tasti)
            return f"Scorciatoia tastiera '{keys_or_text}' eseguita."
        else:
            pyautogui.write(keys_or_text, interval=0.03)
            return f"Digitazione di '{keys_or_text}' completata."
    except Exception as e:
        return f"Impossibile azionare i tasti per '{keys_or_text}': {e}"
