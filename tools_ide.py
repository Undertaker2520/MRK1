import time
import pyautogui
from tools_hardware import analyze_screen

def send_prompt_to_ide_ai(prompt: str, shortcut: str = "ctrl+l") -> str:
    """Invia un comando o una domanda direttamente alla chat dell'AI dell'IDE (VS Code / Antigravity), poi analizza visivamente la risposta.
    
    Args:
        prompt: Il testo da scrivere alla chat dell'AI interna.
        shortcut: Combinazione di tasti per aprire la chat AI (default 'ctrl+l').
    """
    try:
        # 1. Attiva la finestra o apre la chat dell'AI nell'IDE con la scorciatoia da tastiera
        keys = shortcut.lower().split('+')
        pyautogui.hotkey(*keys)
        time.sleep(0.8)
        
        # 2. Digita il prompt dell'utente e invia
        pyautogui.typewrite(prompt, interval=0.02)
        time.sleep(0.2)
        pyautogui.press('enter')
        
        # 3. Attende l'elaborazione dell'AI dell'IDE
        time.sleep(3.5)
        
        # 4. Legge la risposta generata sullo schermo tramite Gemini Vision
        analisi = analyze_screen("Analizza la risposta appena fornita dall'assistente AI dell'IDE e forniscimi un giudizio sintetico e consigli pratici.")
        return f"Prompt inviato all'AI dell'IDE. {analisi}"
        
    except Exception as e:
        return f"Impossibile interagire con l'AI dell'IDE: {e}"