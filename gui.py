import math
import time
import threading
import tkinter as tk
import customtkinter as ctk

from core import chat_with_jarvis
from voice import ascolta, ascolta_wake_word, parla
from config_manager import load_config, set_voice_enabled

ctk.set_appearance_mode("Dark")

COLOR_BG = "#02060E"
COLOR_GRID = "#081424"
COLOR_CYAN = "#00F0FF"
COLOR_GLOW = "#7DF9FF"
COLOR_AMBER = "#FFB300"
COLOR_PURPLE = "#A855F7"
COLOR_DIM = "#1E3A5F"

class JarvisGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("GALILEO")
        self.geometry("900x730")
        self.minsize(800, 650)
        self.configure(fg_color=COLOR_BG)

        self.angle = 0.0
        self.pulse = 0.0
        self.pulse_dir = 1
        self.current_state = "ONLINE"
        self.state_color = COLOR_CYAN
        self.in_sleep_mode = False
        self.is_processing = False
        
        cfg_voice = load_config().get("voice", {})
        self.voice_mode_enabled = cfg_voice.get("enabled", True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # HEADER
        self.header_frame = ctk.CTkFrame(self, fg_color="#050E1A", corner_radius=0, height=45)
        self.header_frame.grid(row=0, column=0, sticky="ew")

        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="GALILEO", 
            text_color=COLOR_CYAN,
            font=ctk.CTkFont(family="Consolas", size=15, weight="bold")
        )
        self.title_label.pack(side="left", padx=20, pady=10)

        self.status_label = ctk.CTkLabel(
            self.header_frame, 
            text="● SYSTEM ONLINE", 
            text_color=COLOR_CYAN,
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold")
        )
        self.status_label.pack(side="right", padx=20, pady=10)

        # CANVAS
        self.canvas_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.canvas_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.canvas_frame, bg=COLOR_BG, highlightthickness=0, bd=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # CONSOLE
        self.bottom_frame = ctk.CTkFrame(self, fg_color="#05101C", corner_radius=12, border_width=1, border_color="#0C253D")
        self.bottom_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.bottom_frame.grid_columnconfigure(0, weight=1)

        self.chat_display = ctk.CTkTextbox(
            self.bottom_frame, height=85, fg_color="#020812", text_color=COLOR_GLOW,
            font=ctk.CTkFont(family="Consolas", size=11), corner_radius=8, border_width=1, border_color="#0A2035"
        )
        self.chat_display.grid(row=0, column=0, columnspan=3, padx=12, pady=(10, 6), sticky="ew")
        self.chat_display.configure(state="disabled")

        self.entry_command = ctk.CTkEntry(
            self.bottom_frame, placeholder_text="[INPUT TESTUALE SECONDARIO...]", 
            fg_color="#040D18", text_color=COLOR_GLOW, font=ctk.CTkFont(family="Consolas", size=11),
            border_color="#0D2E4A", corner_radius=6
        )
        self.entry_command.grid(row=1, column=0, padx=(12, 6), pady=(0, 10), sticky="ew")
        self.entry_command.bind("<Return>", lambda event: self.send_text())

        self.btn_send = ctk.CTkButton(
            self.bottom_frame, text="INVIA", width=80, fg_color="#0A3050", hover_color="#0F4878",
            text_color=COLOR_CYAN, font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            corner_radius=6, command=self.send_text
        )
        self.btn_send.grid(row=1, column=1, padx=4, pady=(0, 10))

        self.btn_voice_toggle = ctk.CTkButton(
            self.bottom_frame, 
            text="🎙 VOCE: ATTIVA" if self.voice_mode_enabled else "🔇 VOCE: DISATTIVATA", 
            width=140, 
            fg_color="#006699" if self.voice_mode_enabled else "#3A1E20",
            hover_color="#0088CC" if self.voice_mode_enabled else "#50282A",
            text_color="#FFFFFF" if self.voice_mode_enabled else "#FF8888",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            corner_radius=6,
            command=self.toggle_voice_mode
        )
        self.btn_voice_toggle.grid(row=1, column=2, padx=(4, 12), pady=(0, 10))

        self.log_message("SYSTEM", "Inizializzazione HUD in corso...")

        self.animate_reactor()

        # BRIEFING TATTICO DI BENVENUTO ALL'AVVIO
        self.after(1500, self._trigger_initial_briefing)

        # Loop vocale permanente
        threading.Thread(target=self._continuous_voice_loop, daemon=True).start()

    def _trigger_initial_briefing(self):
        def _worker_briefing():
            self.is_processing = True
            self.update_status("PROCESSING...", "PROCESSING")
            prompt_sicuro = (
                "Esegui il tool 'get_tactical_briefing' e dai il benvenuto in modo chiaro ed elegante. "
                "NON usare la ricerca web 'search_web'."
            )
            response = chat_with_jarvis(prompt_sicuro)
            if response:
                self.log_message("GALILEO", response)
            self.is_processing = False
            self.update_status("SYSTEM ONLINE", "ONLINE")

        threading.Thread(target=_worker_briefing, daemon=True).start()

    def draw_hud_overlays(self, width, height):
        grid_size = 40
        for x in range(0, width, grid_size):
            self.canvas.create_line(x, 0, x, height, fill=COLOR_GRID, width=1)
        for y in range(0, height, grid_size):
            self.canvas.create_line(0, y, width, y, fill=COLOR_GRID, width=1)

        margin, length = 25, 20
        self.canvas.create_line(margin, margin, margin + length, margin, fill=COLOR_DIM, width=2)
        self.canvas.create_line(margin, margin, margin, margin + length, fill=COLOR_DIM, width=2)
        self.canvas.create_line(width - margin, margin, width - margin - length, margin, fill=COLOR_DIM, width=2)
        self.canvas.create_line(width - margin, margin, width - margin, margin + length, fill=COLOR_DIM, width=2)

        self.canvas.create_text(margin + 30, margin + 10, text="[SYS.CORE: GALILEO_v3]", fill="#205075", font=("Consolas", 9, "bold"), anchor="w")

    def animate_reactor(self):
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width > 50 and height > 50:
            self.draw_hud_overlays(width, height)
            cx, cy = width // 2, height // 2

            if self.current_state == "LISTENING":
                speed = 2.5
                self.state_color = COLOR_AMBER
            elif self.current_state == "PROCESSING":
                speed = 4.5
                self.state_color = COLOR_PURPLE
            else:
                speed = 0.9
                self.state_color = COLOR_CYAN

            self.angle = (self.angle + speed) % 360
            angle_rev = (360 - (self.angle * 1.2)) % 360

            self.pulse += 0.025 * self.pulse_dir
            if self.pulse > 1.0 or self.pulse < 0.0:
                self.pulse_dir *= -1

            r_outer = 145
            for i in range(0, 360, 12):
                rad = math.radians(i + self.angle * 0.5)
                x1 = cx + (r_outer - 10) * math.cos(rad)
                y1 = cy + (r_outer - 10) * math.sin(rad)
                x2 = cx + r_outer * math.cos(rad)
                y2 = cy + r_outer * math.sin(rad)
                self.canvas.create_line(x1, y1, x2, y2, fill=COLOR_DIM, width=2)

            r_mid_out = 125
            self.canvas.create_arc(cx - r_mid_out, cy - r_mid_out, cx + r_mid_out, cy + r_mid_out, start=angle_rev, extent=100, outline=self.state_color, width=2, style=tk.ARC)
            self.canvas.create_arc(cx - r_mid_out, cy - r_mid_out, cx + r_mid_out, cy + r_mid_out, start=angle_rev + 180, extent=100, outline=self.state_color, width=2, style=tk.ARC)

            r_mid_in = 100
            self.canvas.create_arc(cx - r_mid_in, cy - r_mid_in, cx + r_mid_in, cy + r_mid_in, start=self.angle, extent=70, outline=COLOR_GLOW, width=4, style=tk.ARC)
            self.canvas.create_arc(cx - r_mid_in, cy - r_mid_in, cx + r_mid_in, cy + r_mid_in, start=self.angle + 180, extent=70, outline=COLOR_GLOW, width=4, style=tk.ARC)

            r_inner = 75 + (self.pulse * 5)
            self.canvas.create_oval(cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner, outline=self.state_color, width=2)

            r_core = 55
            self.canvas.create_oval(cx - r_core, cy - r_core, cx + r_core, cy + r_core, fill="#020C18", outline=self.state_color, width=3)
            self.canvas.create_text(cx, cy - 2, text="GALILEO", fill="#FFFFFF", font=("Consolas", 15, "bold"))
            self.canvas.create_text(cx, cy + 18, text=self.current_state, fill=self.state_color, font=("Consolas", 8, "bold"))

        self.after(16, self.animate_reactor)

    def update_status(self, text: str, state_key: str = "ONLINE"):
        self.current_state = state_key
        color_map = {"ONLINE": COLOR_CYAN, "LISTENING": COLOR_AMBER, "PROCESSING": COLOR_PURPLE, "SLEEP": "#555555"}
        col = color_map.get(state_key, COLOR_CYAN)
        self.status_label.configure(text=f"● {text}", text_color=col)

    def safe_update_status(self, text: str, state_key: str = "ONLINE"):
        self.after(0, lambda: self.update_status(text, state_key))

    def log_message(self, sender: str, text: str):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"> [{sender}]: {text}\n")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def safe_log_message(self, sender: str, text: str):
        self.after(0, lambda: self.log_message(sender, text))

    def enter_sleep_mode(self):
        if self.in_sleep_mode:
            return
        self.in_sleep_mode = True
        self.safe_update_status("STANDBY / SLEEP", "SLEEP")
        from tools_system import lock_pc
        lock_pc()
        self.withdraw()

    def wake_up(self):
        from tools_system import unlock_pc
        unlock_pc()
        self.deiconify()
        self.lift()
        self.focus_force()
        self.in_sleep_mode = False
        self.safe_update_status("SYSTEM ONLINE", "ONLINE")

    def toggle_voice_mode(self):
        self.voice_mode_enabled = not self.voice_mode_enabled
        set_voice_enabled(self.voice_mode_enabled)
        if self.voice_mode_enabled:
            self.btn_voice_toggle.configure(
                text="🎙 VOCE: ATTIVA",
                fg_color="#006699",
                hover_color="#0088CC",
                text_color="#FFFFFF"
            )
            self.log_message("SYSTEM", "Modalità ascolto vocale (Always On) ATTIVATA.")
            self.update_status("LISTENING FOR 'GALILEO'...", "LISTENING")
        else:
            self.btn_voice_toggle.configure(
                text="🔇 VOCE: DISATTIVATA",
                fg_color="#3A1E20",
                hover_color="#50282A",
                text_color="#FF8888"
            )
            self.log_message("SYSTEM", "Modalità vocale DISATTIVATA. In attesa di input testuali.")
            self.update_status("MODALITÀ TESTUALE (MUTE)", "ONLINE")

    def _continuous_voice_loop(self):
        def voice_status_callback(event_type):
            if event_type == "RECORDING":
                self.safe_update_status("VOCE RILEVATA - IN ASCOLTO...", "LISTENING")
            elif event_type == "RECOGNIZING":
                self.safe_update_status("ANALISI VOCALE...", "PROCESSING")

        while True:
            if self.voice_mode_enabled and not self.is_processing and not self.in_sleep_mode:
                self.safe_update_status("LISTENING FOR 'GALILEO'...", "LISTENING")

                trovato, comando = ascolta_wake_word(status_callback=voice_status_callback)

                if not self.voice_mode_enabled:
                    continue

                if trovato:
                    if self.in_sleep_mode:
                        self.after(0, self.wake_up)

                    if comando:
                        self.safe_log_message("VOICE_INPUT", f"Galileo {comando}")
                        self._handle_voice_command(comando)
                    else:
                        parla("In ascolto.")
                        self.safe_update_status("IN ASCOLTO COMANDO...", "LISTENING")
                        nuovo_comando = ascolta(status_callback=voice_status_callback)
                        if nuovo_comando and self.voice_mode_enabled:
                            self.safe_log_message("VOICE_INPUT", nuovo_comando)
                            self._handle_voice_command(nuovo_comando)
            else:
                if not self.voice_mode_enabled and not self.is_processing and not self.in_sleep_mode:
                    self.safe_update_status("MODALITÀ TESTUALE (MUTE)", "ONLINE")
                time.sleep(0.3)

    def _handle_voice_command(self, comando: str):
        self.is_processing = True
        
        if any(w in comando.lower() for w in ["riposo", "modalità riposo", "vai a riposo", "standby"]):
            parla("Attivazione modalità riposo. Blocco lo schermo e rimango in ascolto.")
            self.after(1000, self.enter_sleep_mode)
        else:
            self.safe_update_status("PROCESSING CORE...", "PROCESSING")
            response = chat_with_jarvis(comando)
            if response:
                self.safe_log_message("GALILEO", response)

        self.is_processing = False
        self.safe_update_status("SYSTEM ONLINE", "ONLINE")

    def send_text(self):
        command = self.entry_command.get().strip()
        if not command:
            return
        self.entry_command.delete(0, "end")
        self.log_message("USER", command)
        threading.Thread(target=self._process_command_text, args=(command,), daemon=True).start()

    def _process_command_text(self, command: str):
        self.is_processing = True
        self.update_status("PROCESSING CORE...", "PROCESSING")
        
        response = chat_with_jarvis(command)
        if response:
            self.log_message("GALILEO", response)

        self.is_processing = False
        self.update_status("SYSTEM ONLINE", "ONLINE")