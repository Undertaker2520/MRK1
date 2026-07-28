import time
import datetime
import threading
from typing import Dict, List, Optional

class AsyncTaskStore:
    """Struttura dati Hash Map (Dizionario Python) con tempo di ricerca O(1) 
    per archiviare e gestire i risultati delle richieste asincrone completate in background.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._completed_tasks: Dict[str, dict] = {} # Hash Table O(1)
        self._task_counter: int = 0
        self._callbacks = []

    def register_completion_callback(self, callback_func):
        """Registra una funzione di callback da eseguire appena la tabella Hash viene aggiornata."""
        with self._lock:
            self._callbacks.append(callback_func)

    def add_completed_task(self, title: str, result: str) -> str:
        """Inserisce il risultato di un task completato nella tabella Hash con tempo O(1) e notifica i listener."""
        task_data = {}
        with self._lock:
            self._task_counter += 1
            key = f"R{self._task_counter}"
            task_data = {
                "key": key,
                "num": self._task_counter,
                "title": title,
                "result": result,
                "viewed": False,
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
            }
            self._completed_tasks[key] = task_data

        # Notifica immediata a tutti i listener registrati appena la tabella Hash si aggiorna
        for cb in self._callbacks:
            try:
                cb(task_data)
            except Exception as e:
                print(f"[CALLBACK HASH STORE ERROR]: {e}")

        return task_data["key"]

    def get_unviewed_tasks(self) -> List[dict]:
        """Restituisce l'elenco dei task completati non ancora visualizzati dall'utente."""
        with self._lock:
            return [task for task in self._completed_tasks.values() if not task["viewed"]]

    def get_task_by_key_or_query(self, query: str) -> Optional[dict]:
        """Ricerca O(1) tramite chiave primaria (es. 'R1', '1') o ricerca per titolo."""
        with self._lock:
            q = query.strip().upper()
            
            # 1. Ricerca diretta O(1) per chiave esatta (es. "R1")
            if q in self._completed_tasks:
                return self._completed_tasks[q]
                
            # 2. Ricerca diretta O(1) per indice numerico (es. "1" -> "R1")
            num_key = f"R{q}"
            if num_key in self._completed_tasks:
                return self._completed_tasks[num_key]
                
            # 3. Ricerca per corrispondenza titolo
            for task in self._completed_tasks.values():
                if q.lower() in task["title"].lower():
                    return task
            return None

    def mark_as_viewed(self, key: str):
        """Segna un task come visualizzato nella tabella Hash."""
        with self._lock:
            if key in self._completed_tasks:
                self._completed_tasks[key]["viewed"] = True

    def clear_all(self):
        """Pulisce la tabella Hash."""
        with self._lock:
            self._completed_tasks.clear()

# Istanza singleton globale dell'Hash Store
task_store = AsyncTaskStore()
