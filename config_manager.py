import json
import os

CONFIG_FILE = "user_config.json"
PROJECTS_FILE = "projects.json"

DEFAULT_CONFIG = {
    "protocols": {
        "work": {
            "configured": False,
            "apps": ["code"],
            "music": "synthwave lofi chill music",
            "brightness": 85,
            "volume": "ABBASSA"
        },
        "gaming": {
            "configured": False,
            "apps_to_close": ["code", "notepad"],
            "brightness": 100,
            "volume": "AUMENTA"
        },
        "night": {
            "configured": False,
            "brightness": 15,
            "volume": "MUTA"
        }
    },
    "voice": {
        "enabled": True,
        "wake_words": ["galileo", "jarvis", "ehi galileo", "hey galileo", "ok galileo", "galilei"],
        "silence_duration": 0.8,
        "max_duration": 10.0,
        "vad_sensitivity": 2.2,
        "language": "it-IT"
    }
}

PROTOCOL_MAP = {
    "work": "work",
    "lavoro": "work",
    "protocollo lavoro": "work",
    "protocollo_lavoro": "work",
    "gaming": "gaming",
    "svago": "gaming",
    "gioco": "gaming",
    "protocollo svago": "gaming",
    "protocollo gaming": "gaming",
    "night": "night",
    "notte": "night",
    "chiusura": "night",
    "protocollo notte": "night"
}

def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            # Ensure defaults for new sections like 'voice'
            updated = False
            for key, val in DEFAULT_CONFIG.items():
                if key not in cfg:
                    cfg[key] = val
                    updated = True
            if updated:
                save_config(cfg)
            return cfg
    except Exception:
        return DEFAULT_CONFIG

def save_config(config: dict):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def update_protocol_preferences(protocol_name: str, key: str, value: str = "") -> str:
    """Aggiorna una preferenza specifica per un protocollo (es: music, apps, brightness).
    
    Args:
        protocol_name: Nome del protocollo ('work', 'gaming', 'night').
        key: Chiave da impostare ('music', 'apps', 'brightness', 'volume').
        value: Valore da assegnare.
    """
    if not value or str(value).strip() == "":
        return "Nessun valore fornito. Chiedi all'utente cosa desidera impostare."

    cfg = load_config()
    clean_name = str(protocol_name).lower().strip()
    target_protocol = PROTOCOL_MAP.get(clean_name, clean_name)
    
    if target_protocol in cfg["protocols"]:
        val_to_store = value
        if key == "apps" and isinstance(value, str):
            val_to_store = [a.strip() for a in value.split(",") if a.strip()]
            
        cfg["protocols"][target_protocol][key] = val_to_store
        cfg["protocols"][target_protocol]["configured"] = True
        save_config(cfg)
        return f"Preferenze aggiornate per il Protocollo '{target_protocol}': {key} impostato su '{val_to_store}'."
    
    return f"Protocollo '{protocol_name}' non trovato."

def set_voice_enabled(enabled: bool):
    cfg = load_config()
    if "voice" not in cfg:
        cfg["voice"] = {}
    cfg["voice"]["enabled"] = enabled
    save_config(cfg)

def load_projects() -> dict:
    if not os.path.exists(PROJECTS_FILE):
        return {}
    try:
        with open(PROJECTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_project_data(project_name: str, data: dict) -> str:
    projects = load_projects()
    p_key = project_name.lower().strip()
    projects[p_key] = data
    with open(PROJECTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(projects, f, indent=4, ensure_ascii=False)
    return f"Progetto '{project_name}' archiviato con successo nel sistema."