# =============================================================================
# File 8: src/gui/control_panel.py
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Optional

from ..utils.config import StreamBlurConfig
from ..utils.performance import PerformanceMonitor

class StreamBlurControlPanel:
    """Pannello di controllo GUI per StreamBlur Pro"""
    
    def __init__(self, app_controller):
        self.app = app_controller  # Riferimento al controller principale
        self.config = app_controller.config
        
        # GUI components
        self.root: Optional[tk.Tk] = None
        self.is_running = False
        
        # Variables per GUI (saranno inizializzate in create_gui)
        self.blur_var: Optional[tk.IntVar] = None
        self.edge_var: Optional[tk.BooleanVar] = None
        self.temporal_var: Optional[tk.BooleanVar] = None
        self.noise_var: Optional[tk.BooleanVar] = None
        self.performance_var: Optional[tk.BooleanVar] = None
        
        # Status labels
        self.status_label = None
        self.fps_label = None
        self.performance_label = None
        
    def create_gui(self):
        """Crea interfaccia grafica"""
        self.root = tk.Tk()
        self.root.title("🎥 StreamBlur Pro v4.0 - Modular Edition")
        
        # Ora che abbiamo root, creiamo le variabili Tkinter
        self.blur_var = tk.IntVar(value=self.config.get('effects.blur_intensity', 15))
        self.edge_var = tk.BooleanVar(value=self.config.get('effects.edge_smoothing', True))
        self.temporal_var = tk.BooleanVar(value=self.config.get('effects.temporal_smoothing', True))
        self.noise_var = tk.BooleanVar(value=self.config.get('effects.noise_reduction', False))
        self.performance_var = tk.BooleanVar(value=self.config.get('ai.performance_mode', False))
        
        width = self.config.get('gui.window_width', 550)
        height = self.config.get('gui.window_height', 500)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(True, True)  # Finestra ridimensionabile
        
        # Tema
        style = ttk.Style()
        style.theme_use(self.config.get('gui.theme', 'clam'))
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        self._create_header(main_frame)
        self._create_status_section(main_frame)
        self._create_control_section(main_frame)
        self._create_settings_section(main_frame)
        self._create_performance_section(main_frame)
        self._create_info_section(main_frame)
        
        # Update loop
        self.is_running = True
        self._start_update_loop()
        
    def _create_header(self, parent):
        """Crea header"""
        # Titolo principale
        title_label = ttk.Label(parent, text="🎥 StreamBlur Pro v4.0", 
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 5))
        
        # Sottotitolo
        subtitle_label = ttk.Label(parent, 
                                  text="Modular Edition - Il Tuo NVIDIA Broadcast per AMD", 
                                  font=('Arial', 10, 'italic'))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
    def _create_status_section(self, parent):
        """Crea sezione status"""
        status_frame = ttk.LabelFrame(parent, text="📊 Status Sistema", padding="15")
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        # Status principale
        self.status_label = ttk.Label(status_frame, text="🔴 Inattivo", 
                                     font=('Arial', 11, 'bold'))
        self.status_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # FPS
        self.fps_label = ttk.Label(status_frame, text="FPS: 0.0")
        self.fps_label.grid(row=1, column=0, sticky=tk.W)
        
        # Performance grade
        self.performance_label = ttk.Label(status_frame, text="Performance: N/A")
        self.performance_label.grid(row=2, column=0, sticky=tk.W)
        
    def _create_control_section(self, parent):
        """Crea sezione controlli"""
        control_frame = ttk.LabelFrame(parent, text="🎮 Controlli", padding="15")
        control_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        # Pulsanti principali
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="🚀 Avvia StreamBlur Pro", 
                                      command=self.start_processing, width=25)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Ferma", 
                                     command=self.stop_processing, width=15)
        self.stop_button.grid(row=0, column=1)
        self.stop_button.config(state='disabled')
        
        # Preview button
        self.preview_button = ttk.Button(button_frame, text="👁️ Preview", 
                                        command=self.toggle_preview, width=15)
        self.preview_button.grid(row=1, column=0, pady=(10, 0))
        
        # Reset settings button
        reset_button = ttk.Button(button_frame, text="🔄 Reset", 
                                 command=self.reset_settings, width=15)
        reset_button.grid(row=1, column=1, pady=(10, 0))
        
    def _create_settings_section(self, parent):
        """Crea sezione impostazioni"""
        settings_frame = ttk.LabelFrame(parent, text="⚙️ Impostazioni Effetti", padding="15")
        settings_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        # Blur intensity
        blur_frame = ttk.Frame(settings_frame)
        blur_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        ttk.Label(blur_frame, text="🌪️ Intensità Blur:").grid(row=0, column=0, sticky=tk.W)
        
        # Assert che le variabili sono già state create
        assert self.blur_var is not None
        assert self.edge_var is not None  
        assert self.temporal_var is not None
        assert self.noise_var is not None
        assert self.performance_var is not None
        
        self.blur_scale = ttk.Scale(blur_frame, from_=1, to=25, 
                                   variable=self.blur_var, orient=tk.HORIZONTAL,
                                   command=self.on_blur_change, length=200)
        self.blur_scale.grid(row=0, column=1, padx=(10, 10))
        
        self.blur_value_label = ttk.Label(blur_frame, text="15")
        self.blur_value_label.grid(row=0, column=2)
        
        # Checkboxes effetti
        self.edge_check = ttk.Checkbutton(settings_frame, text="🎯 Edge Smoothing (Bordi morbidi)",
                                         variable=self.edge_var, command=self.on_edge_toggle)
        self.edge_check.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        self.temporal_check = ttk.Checkbutton(settings_frame, text="⏱️ Temporal Smoothing (Stabilità movimento)",
                                             variable=self.temporal_var, command=self.on_temporal_toggle)
        self.temporal_check.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        self.noise_check = ttk.Checkbutton(settings_frame, text="🔧 Noise Reduction (Rallenta performance)",
                                          variable=self.noise_var, command=self.on_noise_toggle)
        self.noise_check.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # Performance Mode
        self.performance_check = ttk.Checkbutton(settings_frame, text="⚡ Performance Mode (Disattiva per scontorno preciso)",
                                                variable=self.performance_var, command=self.on_performance_toggle)
        self.performance_check.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
    def _create_performance_section(self, parent):
        """Crea sezione performance"""
        perf_frame = ttk.LabelFrame(parent, text="📈 Performance Monitor", padding="10")
        perf_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        # Performance info (sarà aggiornato dinamicamente)
        self.perf_info = ttk.Label(perf_frame, text="Avvia StreamBlur per vedere le statistiche",
                                  font=('Courier', 9))
        self.perf_info.grid(row=0, column=0, sticky=tk.W)
        
    def _create_info_section(self, parent):
        """Crea sezione informazioni"""
        info_frame = ttk.LabelFrame(parent, text="📖 Istruzioni", padding="10")
        info_frame.grid(row=6, column=0, columnspan=2, sticky="ew")
        
        instructions = """🚀 Quick Start:
1. Clicca 'Avvia StreamBlur Pro'
2. Apri Discord/Teams/OBS/Zoom
3. Seleziona 'OBS Virtual Camera' come webcam
4. Regola blur e effetti in tempo reale
5. Goditi il blur professionale!

💡 Nota: La Virtual Camera apparirà come 'OBS Virtual Camera'
ma è il nostro StreamBlur Pro che funziona dietro le quinte!"""
        
        ttk.Label(info_frame, text=instructions, justify=tk.LEFT, 
                 font=('Arial', 8)).grid(row=0, column=0, sticky=tk.W)
    
    # Event handlers
    def start_processing(self):
        """Avvia processing"""
        if self.app.start_processing():
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.preview_button.config(state='normal')
    
    def stop_processing(self):
        """Ferma processing"""
        self.app.stop_processing()
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.preview_button.config(state='disabled')
    
    def toggle_preview(self):
        """Toggle preview window"""
        self.app.toggle_preview()
    
    def reset_settings(self):
        """Reset impostazioni a default"""
        if messagebox.askyesno("Reset Impostazioni", 
                              "Vuoi ripristinare tutte le impostazioni ai valori predefiniti?"):
            self.config.reset_to_defaults()
            self._load_settings_from_config()
            messagebox.showinfo("Reset Completato", "Impostazioni ripristinate ai valori predefiniti!")
    
    def on_blur_change(self, value):
        """Callback cambio blur"""
        intensity = int(float(value))
        self.blur_value_label.config(text=str(intensity))
        self.app.set_blur_intensity(intensity)
    
    def on_edge_toggle(self):
        """Callback toggle edge smoothing"""
        if self.edge_var:
            self.app.set_edge_smoothing(self.edge_var.get())
    
    def on_temporal_toggle(self):
        """Callback toggle temporal smoothing"""
        if self.temporal_var:
            self.app.set_temporal_smoothing(self.temporal_var.get())
    
    def on_noise_toggle(self):
        """Callback toggle noise reduction"""
        if self.noise_var:
            self.app.set_noise_reduction(self.noise_var.get())
    
    def on_performance_toggle(self):
        """Callback toggle performance mode"""
        if self.performance_var:
            performance_mode = self.performance_var.get()
            self.config.set('ai.performance_mode', performance_mode)
            # Mostra messaggio che serve restart
            messagebox.showinfo("Performance Mode", 
                                 "Performance Mode aggiornato! Riavvia StreamBlur per applicare le modifiche.")
    
    def _load_settings_from_config(self):
        """Carica impostazioni dalla configurazione"""
        if self.blur_var:
            self.blur_var.set(self.config.get('effects.blur_intensity', 15))
        if self.edge_var:
            self.edge_var.set(self.config.get('effects.edge_smoothing', True))
        if self.temporal_var:
            self.temporal_var.set(self.config.get('effects.temporal_smoothing', True))
        if self.noise_var:
            self.noise_var.set(self.config.get('effects.noise_reduction', False))
        if self.performance_var:
            self.performance_var.set(self.config.get('ai.performance_mode', False))
    
    def _start_update_loop(self):
        """Avvia loop aggiornamento GUI"""
        self._update_status()
    
    def _update_status(self):
        """Aggiorna status nella GUI"""
        if not self.is_running:
            return
        
        try:
            # Ottieni stats dall'app
            if hasattr(self.app, 'get_stats'):
                stats = self.app.get_stats()
                
                # Aggiorna status
                if stats['is_processing']:
                    if hasattr(self, 'status_label') and self.status_label:
                        self.status_label.config(text="🟢 Attivo - Virtual Camera ON", foreground='green')
                else:
                    if hasattr(self, 'status_label') and self.status_label:
                        self.status_label.config(text="🔴 Inattivo", foreground='red')
                
                # Aggiorna FPS
                fps = stats.get('fps', 0.0)
                fps_color = 'green' if fps >= 25 else 'orange' if fps >= 20 else 'red'
                if hasattr(self, 'fps_label') and self.fps_label:
                    self.fps_label.config(text=f"FPS: {fps:.1f}", foreground=fps_color)
                
                # Aggiorna performance grade
                grade = stats.get('performance_grade', 'N/A')
                if hasattr(self, 'performance_label') and self.performance_label:
                    self.performance_label.config(text=f"Performance: {grade}")
                
                # Aggiorna performance monitor
                perf_text = self._format_performance_info(stats)
                if hasattr(self, 'perf_info') and self.perf_info:
                    self.perf_info.config(text=perf_text)
            
        except Exception as e:
            print(f"⚠️ Errore update GUI: {e}")
        
        # Schedule prossimo update
        if self.root:
            self.root.after(1000, self._update_status)
    
    def _format_performance_info(self, stats):
        """Formatta informazioni performance"""
        try:
            fps = stats.get('fps', 0.0)
            processing_ms = stats.get('processing_time_ms', 0.0)
            cpu = stats.get('cpu_usage', 0.0)
            memory = stats.get('memory_usage', 0.0)
            
            return f"""FPS: {fps:.1f}  |  Processing: {processing_ms:.1f}ms  |  CPU: {cpu:.1f}%  |  RAM: {memory:.1f}%
Frames Sent: {stats.get('frames_sent', 0)}  |  Dropped: {stats.get('frames_dropped', 0)}"""
        except:
            return "Statistiche non disponibili"
    
    def run(self):
        """Avvia GUI"""
        self.create_gui()
        if self.root:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
    
    def on_closing(self):
        """Callback chiusura finestra"""
        self.is_running = False
        self.app.cleanup()
        if self.root:
            self.root.destroy()
