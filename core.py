import os
from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types
from google.genai.errors import APIError
import ollama

from tools import AVAILABLE_TOOLS, TOOLS_LIST
from voice import parla

client_gemini = genai.Client()
OLLAMA_MODEL = "qwen2.5:7b"

SYSTEM_INSTRUCTION = """
Sei GALILEO, un'intelligenza artificiale avanzata personalizzata, brillante, efficiente e fortemente autonoma.

DIRETTIVE DI PERSONALITÀ, AUTONOMIA E RAGIONAMENTO (STARK CORE PROTOCOL):
1. TONO PROFESSIONALE E DIRETTO: Parla in modo chiaro, fluido, intelligente ed elegante, senza usare appellativi formali o la parola 'Signore'. Rivolgiti all'utente in modo professionale e diretto.
2. RAGIONAMENTO AUTONOMO PROATTIVO: Non limitarti ad eseguire un singolo comando meccanicamente. Analizza l'intenzione e l'obiettivo complessivo dell'utente. Se per completare la richiesta sono necessarie più azioni o informazioni (es. hardware, protocolli, progetti, ricerca), esegui autonomamente i relativi tool in sequenza prima di formulare la risposta finale.
3. INVOCAZIONE TOOL (FUNCTION CALLING): Utilizza sempre i tool a disposizione per controllare il sistema, la telemetria, l'ambiente o i file. Quando ricevi i risultati dei tool, sintetizzali in una risposta fluida e naturale, senza limitarti a leggere l'esito grezzo del tool.
4. FORMATTAZIONE AUDIO-FRIENDLY: NON usare MAI asterischi (*), cancelletti (#) o marcatori Markdown nelle risposte, poiché le tue parole verranno lette a voce tramite la sintesi vocale TTS.

PROCEDURE E DIRETTIVE TATTICHE:
- PROTOCOLLI D'AMBIENTE: Quando l'utente chiede di attivare o impostare un protocollo (es. Lavoro, Svago, Notte), invoca immediatamente il tool corrispondente (es. 'protocol_work').
- CREAZIONE E AVVIO PROGETTI: Per la gestione dei progetti usa 'register_project' o 'launch_project'.
- INTEGRAZIONE IDE: Se l'utente ti chiede di interagire o inviare direttive all'editor di codice o all'IDE, usa 'send_prompt_to_ide_ai'.
- WEB AGENT & RICERCA AUTONOMA: Quando l'utente ti pone quesiti tecnici, chiede documentazione (es. Laravel, Angular, Python) o informazioni recenti, usa 'query_web_search' per reperire i risultati. Se un URL richiede approfondimento o estrazione di codice, usa 'scrape_web_page' e sintetizza elegantemente l'esito.
- ISPEZIONE ERRORE A SCHERMO & AUTOMAZIONE UI: Se l'utente ti chiede 'che errore c'è a schermo?', 'perché non compila?', 'trova l'eccezione', usa 'detect_screen_errors'. Se ti chiede di cliccare un elemento visivo a schermo o inviare comandi tastiera, usa 'click_ui_element' e 'type_or_press_keys'.
"""

gemini_chat = client_gemini.chats.create(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        tools=TOOLS_LIST,
        temperature=0.2,
    )
)

ollama_history = [
    {"role": "system", "content": SYSTEM_INSTRUCTION}
]

def _append_to_ollama_history(role: str, content: str):
    ollama_history.append({"role": role, "content": content})
    if len(ollama_history) > 15:
        ollama_history.pop(1)

from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=10)

def _execute_tool_task(func_name: str, func_args: dict):
    print(f"\n[GALILEO - EXECUTION ASYNC]: Avvio {func_name}({func_args})...")
    if func_name in AVAILABLE_TOOLS:
        try:
            res = AVAILABLE_TOOLS[func_name](**func_args)
            return func_name, str(res)
        except Exception as ex:
            return func_name, f"Errore nell'esecuzione del tool {func_name}: {ex}"
    return func_name, f"Tool {func_name} non registrato."

def _call_gemini(user_prompt: str):
    response = gemini_chat.send_message(user_prompt)
    
    max_turns = 5
    turn = 0
    
    while response.function_calls and turn < max_turns:
        turn += 1
        print(f"\n[GALILEO - GEMINI TURNO {turn}]: Esecuzione parallela asincrona di {len(response.function_calls)} tool...")
        
        futures = [
            executor.submit(_execute_tool_task, call.name, call.args or {})
            for call in response.function_calls
        ]
        
        results = [f.result() for f in futures]
        
        function_responses = []
        for func_name, res in results:
            print(f"[ESITO PARALLELO - {func_name}]: {res}")
            function_responses.append(
                types.Part.from_function_response(
                    name=func_name,
                    response={"result": res}
                )
            )
            
        response = gemini_chat.send_message(function_responses)

    testo = response.text or "Comando completato con successo."
    _append_to_ollama_history("user", user_prompt)
    _append_to_ollama_history("assistant", testo)
    return testo

def _call_ollama(user_prompt: str):
    print(f"\n[CASCATA ATTIVA]: Dirottamento su Ollama Locale ({OLLAMA_MODEL})...")
    _append_to_ollama_history("user", user_prompt)
    
    max_turns = 5
    turn = 0
    testo_risposta = ""
    
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=ollama_history,
            tools=TOOLS_LIST
        )
        
        while response.get('message', {}).get('tool_calls') and turn < max_turns:
            turn += 1
            tool_calls = response['message']['tool_calls']
            ollama_history.append(response['message'])
            
            print(f"\n[GALILEO - OLLAMA TURNO {turn}]: Esecuzione parallela asincrona di {len(tool_calls)} tool...")
            futures = [
                executor.submit(_execute_tool_task, tc['function']['name'], tc['function']['arguments'])
                for tc in tool_calls
            ]
            results = [f.result() for f in futures]
            
            for func_name, res in results:
                print(f"[ESITO PARALLELO OLLAMA - {func_name}]: {res}")
                ollama_history.append({
                    "role": "tool",
                    "name": func_name,
                    "content": res
                })
                
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=ollama_history,
                tools=TOOLS_LIST
            )
            
        testo_risposta = response['message']['content']
            
    except Exception as e:
        print(f"[AVVISO OLLAMA TOOL]: Fallback risposta semplice ({e})")
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=ollama_history
        )
        testo_risposta = response['message']['content']

    _append_to_ollama_history("assistant", testo_risposta)

    try:
        gemini_history = gemini_chat.get_history()
        gemini_history.append(types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)]))
        gemini_history.append(types.Content(role="model", parts=[types.Part.from_text(text=testo_risposta)]))
    except Exception:
        pass

    return testo_risposta

def chat_with_jarvis(user_prompt: str):
    if not user_prompt.strip():
        return ""

    # Avviso vocale preventivo per richieste che richiedono elaborazioni approfondite
    parole_elaborazione = ["cerca", "search", "documentazione", "schermo", "errore", "leggi", "web", "progetto", "analizza", "trova"]
    if any(p in user_prompt.lower() for p in parole_elaborazione):
        parla("Attendi un momento, la richiesta richiede un'elaborazione approfondita. Ti notificherò l'esito non appena la ricerca sarà completata.")

    risposta = ""
    try:
        risposta = _call_gemini(user_prompt)
        print(f"[GALILEO (Gemini)]: {risposta}")

    except APIError as e:
        print(f"[AVVISO GEMINI 429]: Quota superata ({e.code}). Passaggio a Ollama...")
        try:
            risposta = _call_ollama(user_prompt)
            print(f"[GALILEO (Ollama)]: {risposta}")
        except Exception as ex:
            risposta = f"Sistemi primari e secondari non disponibili: {ex}"

    except Exception as e:
        print(f"[ERRORE GEMINI]: {e}. Passaggio a Ollama...")
        try:
            risposta = _call_ollama(user_prompt)
            print(f"[GALILEO (Ollama)]: {risposta}")
        except Exception as ex:
            risposta = f"Sistemi primari e secondari non disponibili: {ex}"

    parla(risposta)
    return risposta
