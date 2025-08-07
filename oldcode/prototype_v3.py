#!/usr/bin/env python3
"""
StreamBlur Pro - Prototype v3 - Virtual Camera Edition
LA SVOLTA DEFINITIVA!

Features:
- Virtual Camera integrata (come NVIDIA Broadcast!)
- Background processing separato
- Compatibilità universale (Discord, Teams, OBS, Zoom...)
- Performance ottimizzate con threading intelligente
- Interfaccia di controllo separata dal processing

Adesso funziona esattamente come NVIDIA Broadcast:
1. Avvii StreamBlur Pro
2. In Discord/Teams selezioni "StreamBlur Pro Camera"  
3. Vedi il blur applicato automaticamente!

Ottimizzato per AMD RX 7900 XTX + Ryzen 9 5900X
"""

import cv2
import numpy as np
import mediapipe as mp
import time
from threading import Thread
import queue
from collections import deque
import tkinter as tk
from tkinter import ttk
import pyvirtualcam

class StreamBlurProV3:
    def __init__(self):
        """Inizializza StreamBlur Pro v3 con Virtual Camera"""
        print("🚀 StreamBlur Pro v3 - Virtual Camera Edition")
        print("🎯 Obiettivo: Diventare la tua webcam virtuale preferita!")
        print()
        
        # Configurazione ottimizzata
        self.camera_width = 1280
        self.camera_height = 720
        self.ai_width = 512
        self.ai_height = 288
        self.blur_intensity = 15
        
        # Feature toggles
        self.edge_smoothing = True
        self.temporal_smoothing = True
        self.virtual_camera_active = False
        self.processing_active = False
        
        # Threading e performance
        self.running = False
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # Queue per multi-threading
        self.frame_queue = queue.Queue(maxsize=3)
        self.processed_queue = queue.Queue(maxsize=2)
        self.mask_buffer = deque(maxlen=2)
        
        # Virtual Camera
        self.virtual_cam = None
        
        # Inizializza componenti
        self._init_camera()
        self._init_ai()
        
        print("✅ StreamBlur Pro v3 inizializzato!")
        
    def _init_camera(self):
        """Inizializza webcam fisica"""
        print("📹 Configurando webcam fisica...")
        
        self.cap = cv2.VideoCapture(0)
        
        # Configurazione ottimale
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"📐 Risoluzione input: {actual_width}x{actual_height}")
        
        if not self.cap.isOpened():
            raise Exception("❌ Impossibile aprire la webcam fisica!")
            
    def _init_ai(self):
        """Inizializza MediaPipe AI"""
        print("🤖 Caricando AI per segmentazione...")
        
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self.segmentation = self.mp_selfie_segmentation.SelfieSegmentation(
            model_selection=1
        )
        
        print("✅ AI segmentazione caricata!")
        
    def _init_virtual_camera(self):
        """Inizializza Virtual Camera"""
        try:
            print("📺 Creando Virtual Camera...")
            
            # Crea la virtual camera con pyvirtualcam
            self.virtual_cam = pyvirtualcam.Camera(
                width=self.camera_width,
                height=self.camera_height,
                fps=30,
                fmt=pyvirtualcam.PixelFormat.BGR  # Formato per compatibilità
            )
            
            print("✅ Virtual Camera creata!")
            print(f"🎯 Dispositivo: {self.virtual_cam.device}")
            print()
            print("🎉 SUCCESSO! Ora puoi usare 'StreamBlur Pro' come webcam in:")
            print("   - Discord")
            print("   - Microsoft Teams") 
            print("   - OBS Studio")
            print("   - Zoom")
            print("   - Google Meet")
            print("   - E qualsiasi altra app!")
            print()
            
            self.virtual_camera_active = True
            return True
            
        except Exception as e:
            print(f"❌ Errore creazione Virtual Camera: {e}")
            print("💡 Assicurati di aver installato OBS Virtual Camera o simili")
            return False
    
    def _calculate_fps(self):
        """Calcola FPS"""
        self.fps_counter += 1
        current_time = time.time()
        elapsed = current_time - self.fps_start_time
        
        if elapsed >= 1.0:
            self.current_fps = self.fps_counter / elapsed
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def _apply_edge_smoothing(self, mask):
        """Edge smoothing ottimizzato"""
        if not self.edge_smoothing:
            return mask
            
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask_smooth = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask_smooth = cv2.GaussianBlur(mask_smooth, (3, 3), 0.5)
        return mask_smooth
    
    def _apply_temporal_smoothing(self, mask):
        """Temporal smoothing"""
        if not self.temporal_smoothing:
            return mask
            
        self.mask_buffer.append(mask.copy())
        
        if len(self.mask_buffer) >= 2:
            smoothed_mask = (0.7 * mask.astype(np.float32) + 
                           0.3 * self.mask_buffer[-2].astype(np.float32))
            return smoothed_mask.astype(np.uint8)
        
        return mask
    
    def _apply_blur(self, frame, mask):
        """Applica blur ottimizzato"""
        mask_normalized = mask.astype(np.float32) / 255.0
        
        # Kernel size sempre dispari
        kernel_size = max(3, self.blur_intensity * 2 + 1)
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        # Blur dello sfondo
        blurred_bg = cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
        
        # Mask a 3 canali con blur leggero per transizioni smooth
        mask_3ch = np.stack([mask_normalized] * 3, axis=-1)
        mask_blurred = cv2.GaussianBlur(mask_3ch, (3, 3), 1)
        
        # Componi risultato
        result = frame * mask_blurred + blurred_bg * (1 - mask_blurred)
        return result.astype(np.uint8)
    
    def _capture_thread(self):
        """Thread per cattura frame dalla webcam fisica"""
        print("📹 Avviato thread cattura webcam...")
        
        while self.running:
            ret, frame = self.cap.read()
            if ret and self.processing_active:
                if not self.frame_queue.full():
                    self.frame_queue.put(frame)
            time.sleep(0.001)
    
    def _processing_thread(self):
        """Thread per processing AI e blur"""
        print("🤖 Avviato thread processing AI...")
        
        while self.running:
            if not self.frame_queue.empty() and self.processing_active:
                frame = self.frame_queue.get()
                
                try:
                    # Processing AI
                    ai_frame = cv2.resize(frame, (self.ai_width, self.ai_height))
                    rgb_frame = cv2.cvtColor(ai_frame, cv2.COLOR_BGR2RGB)
                    
                    # Segmentazione
                    results = self.segmentation.process(rgb_frame)
                    mask = results.segmentation_mask
                    
                    # Ridimensiona mask
                    mask_resized = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
                    mask_resized = (mask_resized * 255).astype(np.uint8)
                    
                    # Applica miglioramenti
                    mask_enhanced = self._apply_edge_smoothing(mask_resized)
                    mask_enhanced = self._apply_temporal_smoothing(mask_enhanced)
                    
                    # Applica blur
                    processed_frame = self._apply_blur(frame, mask_enhanced)
                    
                    # Invia alla virtual camera
                    if not self.processed_queue.full():
                        self.processed_queue.put(processed_frame)
                        
                except Exception as e:
                    print(f"⚠️ Errore processing: {e}")
                    # In caso di errore, invia frame originale
                    if not self.processed_queue.full():
                        self.processed_queue.put(frame)
            
            time.sleep(0.001)
    
    def _virtual_camera_thread(self):
        """Thread per invio frame alla virtual camera"""
        print("📺 Avviato thread Virtual Camera...")
        
        while self.running and self.virtual_camera_active:
            if not self.processed_queue.empty():
                processed_frame = self.processed_queue.get()
                
                try:
                    # Invia frame alla virtual camera
                    if self.virtual_cam is not None:
                        self.virtual_cam.send(processed_frame)
                        self._calculate_fps()
                        
                except Exception as e:
                    print(f"⚠️ Errore Virtual Camera: {e}")
            
            time.sleep(0.001)
    
    def start_processing(self):
        """Avvia il processing in background"""
        if self.processing_active:
            print("⚠️ Processing già attivo!")
            return
            
        print("🎬 Avviando StreamBlur Pro...")
        
        # Inizializza virtual camera
        if not self._init_virtual_camera():
            print("❌ Impossibile creare Virtual Camera")
            return False
        
        # Avvia tutti i thread
        self.running = True
        self.processing_active = True
        
        # Thread per cattura
        self.capture_thread = Thread(target=self._capture_thread, daemon=True)
        self.capture_thread.start()
        
        # Thread per processing
        self.processing_thread = Thread(target=self._processing_thread, daemon=True) 
        self.processing_thread.start()
        
        # Thread per virtual camera
        self.virtual_thread = Thread(target=self._virtual_camera_thread, daemon=True)
        self.virtual_thread.start()
        
        print("✅ StreamBlur Pro attivo!")
        print("🎯 Ora puoi usare 'StreamBlur Pro' come webcam nelle tue app!")
        
        return True
    
    def stop_processing(self):
        """Ferma il processing"""
        print("⏹️ Fermando StreamBlur Pro...")
        
        self.processing_active = False
        self.running = False
        
        # Chiudi virtual camera
        if self.virtual_cam is not None:
            self.virtual_cam.close()
            self.virtual_cam = None
            self.virtual_camera_active = False
        
        print("✅ StreamBlur Pro fermato!")
    
    def get_status(self):
        """Ottieni stato corrente"""
        return {
            'processing_active': self.processing_active,
            'virtual_camera_active': self.virtual_camera_active,
            'fps': self.current_fps,
            'blur_intensity': self.blur_intensity,
            'edge_smoothing': self.edge_smoothing,
            'temporal_smoothing': self.temporal_smoothing
        }
    
    def set_blur_intensity(self, intensity):
        """Imposta intensità blur"""
        self.blur_intensity = max(1, min(25, intensity))
    
    def toggle_edge_smoothing(self):
        """Toggle edge smoothing"""
        self.edge_smoothing = not self.edge_smoothing
    
    def toggle_temporal_smoothing(self):
        """Toggle temporal smoothing"""
        self.temporal_smoothing = not self.temporal_smoothing
        if not self.temporal_smoothing:
            self.mask_buffer.clear()
    
    def cleanup(self):
        """Pulizia finale"""
        self.stop_processing()
        
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        
        print("🧹 Cleanup completato!")

class StreamBlurControlGUI:
    """Interfaccia di controllo per StreamBlur Pro v3"""
    
    def __init__(self):
        self.stream_blur = StreamBlurProV3()
        self.create_gui()
        
    def create_gui(self):
        """Crea interfaccia grafica"""
        self.root = tk.Tk()
        self.root.title("🎥 StreamBlur Pro v3 - Virtual Camera Control")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🎥 StreamBlur Pro v3", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, text="Virtual Camera Edition", 
                                  font=('Arial', 10, 'italic'))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="📊 Status", padding="10")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.status_label = ttk.Label(status_frame, text="🔴 Inattivo")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.fps_label = ttk.Label(status_frame, text="FPS: 0.0")
        self.fps_label.grid(row=1, column=0, sticky=tk.W)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        self.start_button = ttk.Button(button_frame, text="🚀 Avvia Virtual Camera", 
                                      command=self.start_processing, width=20)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Ferma", 
                                     command=self.stop_processing, width=15)
        self.stop_button.grid(row=0, column=1)
        self.stop_button.config(state='disabled')
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Impostazioni", padding="10")
        settings_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Blur intensity
        ttk.Label(settings_frame, text="🌪️ Intensità Blur:").grid(row=0, column=0, sticky=tk.W)
        self.blur_var = tk.IntVar(value=15)
        self.blur_scale = ttk.Scale(settings_frame, from_=1, to=25, 
                                   variable=self.blur_var, orient=tk.HORIZONTAL,
                                   command=self.on_blur_change, length=200)
        self.blur_scale.grid(row=0, column=1, padx=(10, 0))
        
        self.blur_value_label = ttk.Label(settings_frame, text="15")
        self.blur_value_label.grid(row=0, column=2, padx=(10, 0))
        
        # Checkboxes
        self.edge_var = tk.BooleanVar(value=True)
        self.edge_check = ttk.Checkbutton(settings_frame, text="🎯 Edge Smoothing",
                                         variable=self.edge_var, 
                                         command=self.on_edge_toggle)
        self.edge_check.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        self.temporal_var = tk.BooleanVar(value=True)
        self.temporal_check = ttk.Checkbutton(settings_frame, text="⏱️ Temporal Smoothing",
                                             variable=self.temporal_var,
                                             command=self.on_temporal_toggle)
        self.temporal_check.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # Instructions
        info_frame = ttk.LabelFrame(main_frame, text="📖 Istruzioni", padding="10")
        info_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        instructions = """1. Clicca 'Avvia Virtual Camera' 
2. Apri Discord/Teams/OBS
3. Seleziona 'StreamBlur Pro' come webcam
4. Goditi il blur in tempo reale! 🎉"""
        
        ttk.Label(info_frame, text=instructions, justify=tk.LEFT).grid(row=0, column=0, sticky=tk.W)
        
        # Update loop
        self.update_status()
        
    def start_processing(self):
        """Avvia processing"""
        if self.stream_blur.start_processing():
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            
    def stop_processing(self):
        """Ferma processing"""
        self.stream_blur.stop_processing()
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
    def on_blur_change(self, value):
        """Callback cambio blur"""
        intensity = int(float(value))
        self.blur_value_label.config(text=str(intensity))
        self.stream_blur.set_blur_intensity(intensity)
        
    def on_edge_toggle(self):
        """Callback toggle edge smoothing"""
        self.stream_blur.toggle_edge_smoothing()
        
    def on_temporal_toggle(self):
        """Callback toggle temporal smoothing"""
        self.stream_blur.toggle_temporal_smoothing()
        
    def update_status(self):
        """Aggiorna status GUI"""
        status = self.stream_blur.get_status()
        
        if status['processing_active']:
            self.status_label.config(text="🟢 Attivo - Virtual Camera ON")
            self.fps_label.config(text=f"FPS: {status['fps']:.1f}")
        else:
            self.status_label.config(text="🔴 Inattivo")
            self.fps_label.config(text="FPS: 0.0")
        
        # Schedule prossimo update
        self.root.after(1000, self.update_status)
        
    def run(self):
        """Avvia GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """Callback chiusura finestra"""
        self.stream_blur.cleanup()
        self.root.destroy()

def main():
    """Entry point v3"""
    print("🚀 StreamBlur Pro v3 - Virtual Camera Edition")
    print("🎯 La tua alternativa open-source a NVIDIA Broadcast!")
    print()
    
    try:
        # Avvia GUI di controllo
        gui = StreamBlurControlGUI()
        gui.run()
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()