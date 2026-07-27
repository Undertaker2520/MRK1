import os
import subprocess
import psutil
import ctypes
import time
import pyautogui

APP_ALIASES = {
    "calcolatrice": "calc",
    "calculator": "calc",
    "blocco note": "notepad",
    "blocco-note": "notepad",
    "notepad": "notepad",
    "esplora risorse": "explorer",
    "gestione attività": "taskmgr",
    "gestione attivita": "taskmgr",
    "cmd": "cmd",
    "prompt dei comandi": "cmd",
    "terminale": "powershell",
    "code": "code",
    "vs code": "code",
    "vscode": "code",
    "antigravity": r"C:\Users\nicho\AppData\Local\Programs\Antigravity\Antigravity.exe",
    "google antigravity": r"C:\Users\nicho\AppData\Local\Programs\Antigravity\Antigravity.exe"
}

def open_application(app_name: str) -> str:
    """Apre un'applicazione sul sistema operativo Windows.
    
    Args:
        app_name: Il nome dell'applicazione (es. 'calcolatrice', 'notepad', 'chrome', 'code').
    """
    clean_app = app_name.lower().strip()
    target_exec = APP_ALIASES.get(clean_app, clean_app)
    
    try:
        subprocess.Popen(f'start "" "{target_exec}"', shell=True)
        return f"Applicazione '{app_name}' avviata."
    except Exception as e:
        return f"Errore nell'apertura di '{app_name}': {e}"

def close_application(process_name: str) -> str:
    """Termina un'applicazione su Windows."""
    closed_count = 0
    clean_name = process_name.lower().replace(".exe", "")
    target_name = APP_ALIASES.get(clean_name, clean_name)
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if target_name in proc.info['name'].lower():
                proc.kill()
                closed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if closed_count > 0:
        return f"Terminati {closed_count} processi relativi a '{process_name}'."
    return f"Nessun processo attivo trovato corrispondente a '{process_name}'."

def open_file(file_name_or_path: str, search_directory: str = "") -> str:
    """Apre un file o documento nel percorso indicato o nelle cartelle utente."""
    if os.path.exists(file_name_or_path):
        try:
            os.startfile(file_name_or_path)
            return f"File '{file_name_or_path}' aperto correttamente."
        except Exception as e:
            return f"Errore nell'apertura di '{file_name_or_path}': {e}"

    clean_name = os.path.basename(file_name_or_path).lower().strip()
    user_home = os.path.expanduser('~')
    
    directories_to_search = []
    if search_directory and os.path.exists(search_directory):
        directories_to_search.append(search_directory)
    else:
        directories_to_search = [
            os.path.join(user_home, 'Desktop'),
            os.path.join(user_home, 'Documents'),
            os.path.join(user_home, 'Downloads'),
            os.getcwd()
        ]

    for target_dir in directories_to_search:
        if not os.path.exists(target_dir):
            continue
        try:
            for root, dirs, files in os.walk(target_dir):
                for f in files:
                    f_no_ext, _ = os.path.splitext(f)
                    if clean_name == f.lower() or clean_name == f_no_ext.lower() or clean_name in f.lower():
                        full_path = os.path.join(root, f)
                        os.startfile(full_path)
                        return f"File '{f}' trovato in '{root}' e aperto correttamente."
        except Exception:
            continue

    return f"Impossibile trovare il file '{file_name_or_path}'."

def lock_pc() -> str:
    """Blocca lo schermo di Windows."""
    try:
        ctypes.windll.user32.LockWorkStation()
        return "Schermo del PC bloccato."
    except Exception as e:
        return f"Impossibile bloccare lo schermo: {e}"

def unlock_pc() -> str:
    """Sblocca lo schermo di Windows digitando la password del file .env."""
    password = os.getenv("PC_PASSWORD", "")
    if not password:
        return "Nessuna password impostata nel file .env."
    try:
        pyautogui.press('space')
        time.sleep(0.6)
        pyautogui.press('space')
        time.sleep(0.6)
        pyautogui.typewrite(password, interval=0.04)
        pyautogui.press('enter')
        return "Procedura di sblocco inviata."
    except Exception as e:
        return f"Errore durante lo sblocco del PC: {e}"

def suspend_pc() -> str:
    """Mette il sistema operativo Windows in modalità Sospensione."""
    try:
        ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
        return "Sospensione del sistema avviata."
    except Exception as e:
        return f"Impossibile mettere il PC in sospensione: {e}"

def shutdown_pc() -> str:
    """Spegne il computer dopo 5 secondi."""
    try:
        subprocess.run(["shutdown", "/s", "/t", "5"], check=True)
        return "Arresto del sistema avviato."
    except Exception as e:
        return f"Impossibile spegnere il computer: {e}"

def restart_pc() -> str:
    """Riavvia il computer dopo 5 secondi."""
    try:
        subprocess.run(["shutdown", "/r", "/t", "5"], check=True)
        return "Riavvio del sistema avviato."
    except Exception as e:
        return f"Impossibile riavviare il computer: {e}"