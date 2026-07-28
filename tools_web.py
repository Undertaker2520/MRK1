import time
import threading
import webbrowser
import requests
from bs4 import BeautifulSoup
import pyautogui
import pyperclip
import pywhatkit

http_session = requests.Session()
http_session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
})

def query_web_search(query: str, num_results: int = 5) -> str:
    """Esegue una ricerca web headless per reperire informazioni, documentazione tecnica, articoli o soluzioni a problemi di programmazione senza aprire la finestra del browser.
    
    Usa questo tool quando devi cercare informazioni aggiornate, documentazione di librerie/framework (es. Laravel, Angular, Python, React), errori di codice o notizie sul web per poi riassumerle all'utente.
    
    Args:
        query: Parola chiave o domanda da cercare sul web.
        num_results: Numero massimo di risultati da estrarre (default 5).
    """
    try:
        url = 'https://html.duckduckgo.com/html/'
        response = http_session.post(url, data={'q': query}, timeout=4.0)
        
        if response.status_code not in [200, 202]:
            return f"Errore nel servizio di ricerca (HTTP {response.status_code})."
            
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for res in soup.select('.result'):
            if len(results) >= num_results:
                break
                
            title_elem = res.select_one('.result__title')
            snippet_elem = res.select_one('.result__snippet')
            url_elem = res.select_one('.result__url')
            
            if not title_elem or not snippet_elem:
                continue
                
            title = title_elem.get_text(strip=True)
            snippet = snippet_elem.get_text(strip=True)
            link_url = url_elem.get_text(strip=True) if url_elem else ""
            
            if "AdViewing ads" in snippet or "AdViewing ads" in title:
                continue
                
            results.append(f"• Titolo: {title}\n  URL: {link_url}\n  Estratto: {snippet}")
            
        if not results:
            return f"Nessun risultato trovato per la ricerca: '{query}'."
            
        return f"Risultati della ricerca web per '{query}':\n\n" + "\n\n".join(results)
        
    except Exception as e:
        return f"Impossibile completare la ricerca web per '{query}': {e}"

def background_web_search(query: str) -> str:
    """Avvia una ricerca web in background senza bloccare la conversazione. 
    L'esito verrà salvato nella tabella Hash O(1) e notificato all'utente al termine del prompt.
    
    Args:
        query: L'argomento o la domanda da cercare sul web in background.
    """
    from async_task_store import task_store
    def _worker():
        res = query_web_search(query)
        task_store.add_completed_task(f"Ricerca web su '{query}'", res)

    threading.Thread(target=_worker, daemon=True).start()
    return f"Ricerca su '{query}' presa in carico ed avviata in background."

def scrape_web_page(url: str, max_chars: int = 3500) -> str:
    """Estrae e pulisce il testo da una pagina web specifica (es. documentazione tecnica, tutorial, pagina StackOverflow, GitHub) dato il suo URL.
    
    Usa questo tool dopo 'query_web_search' se desideri approfondire una pagina web specifica o estrarre un esempio di codice dettagliato.
    
    Args:
        url: L'URL completo della pagina web da leggere (es. 'https://laravel.com/docs/11.x/rate-limiting').
        max_chars: Limite massimo di caratteri da restituire (default 3500).
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
        
    try:
        res = requests.get(url, headers=HEADERS, timeout=7)
        if res.status_code != 200:
            return f"Impossibile accedere alla pagina web (HTTP {res.status_code})."
            
        soup = BeautifulSoup(res.text, 'html.parser')
        
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'noscript', 'svg', 'form']):
            element.decompose()
            
        text = soup.get_text(separator='\n', strip=True)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_content = '\n'.join(lines)
        
        if len(clean_content) > max_chars:
            clean_content = clean_content[:max_chars] + "\n...[Contenuto troncato per brevità]"
            
        return f"Contenuto della pagina ({url}):\n\n{clean_content}"
        
    except Exception as e:
        return f"Errore durante l'estrazione della pagina {url}: {e}"

def search_web(query: str, platform: str = "google") -> str:
    """Apre il browser grafico dell'utente per mostrare visivamente una pagina di ricerca."""
    try:
        if platform.lower() == "youtube":
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        else:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            
        webbrowser.open(url)
        return f"Ricerca per '{query}' avviata su {platform} nel browser."
    except Exception as e:
        return f"Errore nell'apertura del browser: {e}"

def play_youtube_video(query: str) -> str:
    """Cerca e RIPRODUCE DIRETTAMENTE una canzone, musica o video specifico su YouTube."""
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
    """Legge il testo dagli appunti di Windows."""
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