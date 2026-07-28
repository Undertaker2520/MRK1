import os
import subprocess
from config_manager import save_project_data, load_projects
from tools_hardware import brightness_control
from tools_system import open_application

def register_project(name: str, project_type: str, path: str, recommended_tools: str, specs: str) -> str:
    """Registra un nuovo progetto nel database locale di GALILEO con tutte le sue specifiche.
    
    Args:
        name: Nome identificativo del progetto.
        project_type: Tipo (es. Web App PHP/Laravel, Pentesting Lab, Script Python, C#/.NET).
        path: Cartella di destinazione del progetto sul PC.
        recommended_tools: Strumenti/IDE consigliati (es. VS Code, Antigravity, Docker, PhpStorm).
        specs: Breve riassunto dei requisiti e delle funzionalità del progetto.
    """
    if not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            return f"Impossibile creare la cartella '{path}': {e}"

    data = {
        "name": name,
        "type": project_type,
        "path": path,
        "tools": recommended_tools,
        "specs": specs
    }
    
    save_project_data(name, data)
    return f"Progetto '{name}' registrato correttamente. Cartella configurata in '{path}'."

def launch_project(name: str) -> str:
    """Avvia un progetto esistente: apre la directory di sviluppo, l'IDE e fornisce un recap tattico.
    
    Args:
        name: Nome del progetto da avviare.
    """
    projects = load_projects()
    p_key = name.lower().strip()
    
    if p_key not in projects:
        return f"Nessun progetto trovato corrispondente a '{name}'."
        
    p = projects[p_key]
    path = p.get("path", "")
    tools = p.get("tools", "code")
    
    # Apre l'IDE nella cartella del progetto se il percorso esiste
    if os.path.exists(path):
        try:
            subprocess.Popen(f'code "{path}"', shell=True)
        except Exception:
            open_application("code")
            
    recap = (
        f"Avvio del progetto '{p['name']}' in corso. "
        f"Tipologia: {p['type']}. "
        f"Percorso principale: {path}. "
        f"Requisiti fondamentali: {p['specs']}. "
        f"Ambiente di sviluppo pronto."
    )
    return recap