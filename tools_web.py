import time
import threading
import webbrowser
import pyautogui
import pyperclip
import pywhatkit

def search_web(query: str, platform: str = "google") -> str:
    """Apre il browser web per mostrare i risultati di una ricerca.
    
    IMPORTANTE: Usa questa funzione SOLO ED ESCLUSIVAMENTE se l'utente ti chiede ESPLICITAMENTE di aprire il browser o effettuare una ricerca sul web (es: 'cerca su Google X', 'apri il browser e cerca Y').
    NON usare MAI questa funzione per rispondere a domande di cultura generale, curiosità o informazioni (es: 'chi è il presidente...', 'qual è la capitale...'). Per quelle domande rispondi direttamente a voce senza usare alcun tool.
    
    Args:
        query: Testo da cercare.
        platform: 'google' oppure 'youtube'.
    """
    try:
        if platform.lower() == "youtube":
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        else:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            
        webbrowser.open(url)
        return f"Ricerca per '{query}' avviata su {platform}."
    except Exception as e:
        return f"Errore nell'apertura del browser: {e}"

def play_youtube_video(query: str) -> str:
    """Cerca e RIPRODUCE DIRETTAMENTE una canzone, musica o video specifico su YouTube.
    
    Usa questo tool quando l'utente ti chiede di mettere della musica o riprodurre un video (es: 'metti i Queen', 'fammi sentire...').
    
    Args:
        query: Titolo della canzone, artista o video.
    """
    try:
        pywhatkit.playonyt(query)
        return f"Riproduzione di '{query}' avviata direttamente su YouTube."
    except Exception as e:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Aperta la pagina di YouTube per '{query}'."

def media_control(action: str) -> str:
    """Gestisce la riproduzione multimediale (PLAY, PAUSA, NEXT, PREV)."""
    act = action.lower()
    if act in ["play", "pause", "playpause", "pausa"]:
        pyautogui.press("playpause")
        return "Riproduzione multimediale alternata."
    elif act in ["next", "successivo", "avanti"]:
        pyautogui.press("nexttrack")
        return "Traccia successiva."
    elif act in ["prev", "precedente", "indietro"]:
        pyautogui.press("prevtrack")
        return "Traccia precedente."
    else:
        return f"Azione multimediale '{action}' non riconosciuta."

def read_clipboard() -> str:
    """Legge il testo dagli appunti di Windows.
    
    IMPORTANTE: Usa questo tool SOLO ED ESCLUSIVAMENTE se l'utente chiede esplicitamente 'cosa c'è negli appunti', 'leggi gli appunti' o 'cosa ho copiato'.
    NON usare MAI questo tool per domande personali, opinioni o conversazione.
    """
    try:
        text = pyperclip.paste()
        if text.strip():
            return f"Contenuto negli appunti: {text[:300]}"
        return "Gli appunti di sistema sono vuoti."
    except Exception as e:
        return f"Impossibile leggere gli appunti: {e}"

def set_timer(seconds: int, message: str = "Timer scaduto") -> str:
    """Imposta un timer in background."""
    def _timer_worker():
        time.sleep(seconds)
        from voice import parla
        parla(f"Attenzione. {message}")

    threading.Thread(target=_timer_worker, daemon=True).start()
    return f"Timer impostato per {seconds} secondi con messaggio: '{message}'."