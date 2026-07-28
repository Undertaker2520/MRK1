from config_manager import load_config, update_protocol_preferences
from tools_hardware import brightness_control, volume_control
from tools_system import open_application, close_application, lock_pc
from tools_web import play_youtube_video

def sanitize_app_list(raw_apps) -> list[str]:
    """Pulisce la lista o stringa di app rimuovendo parentesi quadre, apici e virgolette."""
    cleaned_apps = []
    
    if isinstance(raw_apps, str):
        # Rimuove parentesi quadre e apici residui: "['vs', 'antigravity']" -> "vs, antigravity"
        clean_str = raw_apps.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
        cleaned_apps = [a.strip() for a in clean_str.split(",") if a.strip()]
    elif isinstance(raw_apps, list):
        for item in raw_apps:
            clean_item = str(item).replace("[", "").replace("]", "").replace("'", "").replace('"', "").strip()
            if clean_item:
                cleaned_apps.append(clean_item)
                
    return cleaned_apps

def is_protocol_configured(cfg: dict) -> bool:
    if cfg.get("configured", False):
        return True
    if cfg.get("apps") or cfg.get("music") or cfg.get("apps_to_close"):
        return True
    return False

def protocol_work() -> str:
    """Esegue le azioni del Protocollo Lavoro: hardware, applicazioni ed avvio musica."""
    cfg = load_config()["protocols"]["work"]
    
    if not is_protocol_configured(cfg):
        return "Non ho ancora registrato le preferenze per il Protocollo Lavoro. Quali applicazioni o IDE desideri utilizzare e quale musica vuoi ascoltare?"

    results = []
    # 1. Hardware
    results.append(brightness_control(cfg.get("brightness", 85)))
    results.append(volume_control(cfg.get("volume", "ABBASSA")))
    
    # 2. Apertura Applicazioni / IDE (con sanificazione della lista)
    apps = sanitize_app_list(cfg.get("apps", ["code"]))
    for app in apps:
        results.append(open_application(app))
        
    # 3. Avvio Musica YouTube
    music = cfg.get("music", "")
    if music:
        results.append(play_youtube_video(music))
        
    return "Protocollo Lavoro eseguito: ambiente configurato, applicazioni avviate e musica in riproduzione."

def protocol_gaming() -> str:
    """Esegue le azioni del Protocollo Svago/Gaming."""
    cfg = load_config()["protocols"]["gaming"]
    
    apps_to_close = sanitize_app_list(cfg.get("apps_to_close", ["code", "notepad", "calc"]))
    for app in apps_to_close:
        close_application(app)
        
    brightness_control(cfg.get("brightness", 100))
    volume_control(cfg.get("volume", "AUMENTA"))
    
    return "Protocollo Svago attivato. Ambiente pronto e risorse liberate."

def protocol_night() -> str:
    """Esegue le azioni del Protocollo Notte."""
    cfg = load_config()["protocols"]["night"]
    brightness_control(cfg.get("brightness", 15))
    volume_control(cfg.get("volume", "MUTA"))
    lock_pc()
    return "Protocollo Notte completato. Buonanotte."