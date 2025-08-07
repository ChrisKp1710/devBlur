#!/usr/bin/env python3
"""
Demo UI moderna di StreamBlur Pro
Mostra l'anteprima della nuova interfaccia utente
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import time
from threading import Thread

# Aggiungi il path del progetto
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

class DemoStreamBlurApp:
    """Versione demo di StreamBlur Pro per test UI"""
    
    def __init__(self):
        self.config = DemoConfig()
        self.is_processing = False
        self.demo_stats = {
            'fps': 0.0,
            'processing_time_ms': 0.0,
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'frames_sent': 0,
            'frames_dropped': 0,
            'performance_grade': 'N/A',
            'is_processing': False
        }
        
    def start_processing(self):
        """Simula avvio processing"""
        print("🚀 [DEMO] Avvio StreamBlur Pro...")
        self.is_processing = True
        self.demo_stats['is_processing'] = True
        
        # Simula stats realistiche in background
        Thread(target=self._simulate_stats, daemon=True).start()
        return True
        
    def stop_processing(self):
        """Simula stop processing"""
        print("⏹️ [DEMO] Fermata StreamBlur Pro")
        self.is_processing = False
        self.demo_stats['is_processing'] = False
        self.demo_stats['fps'] = 0.0
        
    def toggle_preview(self):
        """Simula toggle preview"""
        print("👁️ [DEMO] Toggle preview")
        messagebox.showinfo("Preview", "In modalità demo, questa funzione mostrerebbe l'anteprima video!")
        
    def set_blur_intensity(self, intensity):
        """Simula cambio intensità blur"""
        print(f"🌪️ [DEMO] Blur intensity: {intensity}")
        
    def set_edge_smoothing(self, enabled):
        """Simula toggle edge smoothing"""
        print(f"🎯 [DEMO] Edge smoothing: {enabled}")
        
    def set_temporal_smoothing(self, enabled):
        """Simula toggle temporal smoothing"""
        print(f"⏱️ [DEMO] Temporal smoothing: {enabled}")
        
    def set_noise_reduction(self, enabled):
        """Simula toggle noise reduction"""
        print(f"🔧 [DEMO] Noise reduction: {enabled}")
        
    def get_stats(self):
        """Ritorna stats simulate"""
        return self.demo_stats
        
    def cleanup(self):
        """Cleanup demo"""
        print("🧹 [DEMO] Cleanup")
        self.is_processing = False
        
    def _simulate_stats(self):
        """Simula statistiche realistiche"""
        import random
        import time
        
        frame_count = 0
        while self.is_processing:
            # Simula FPS variabile ma realistico
            base_fps = 28.5
            fps_variation = random.uniform(-2.0, 3.0)
            self.demo_stats['fps'] = max(0, base_fps + fps_variation)
            
            # Simula processing time
            self.demo_stats['processing_time_ms'] = random.uniform(15.0, 35.0)
            
            # Simula utilizzo risorse
            self.demo_stats['cpu_usage'] = random.uniform(25.0, 45.0)
            self.demo_stats['memory_usage'] = random.uniform(18.0, 25.0)
            
            # Incrementa frame counter
            frame_count += int(self.demo_stats['fps'])
            self.demo_stats['frames_sent'] = frame_count
            
            # Simula qualche frame droppato occasionalmente
            if random.random() < 0.1:  # 10% di probabilità
                self.demo_stats['frames_dropped'] += 1
                
            # Performance grade basato su FPS
            fps = self.demo_stats['fps']
            if fps >= 25:
                self.demo_stats['performance_grade'] = "🟢 Eccellente"
            elif fps >= 20:
                self.demo_stats['performance_grade'] = "🟡 Buono" 
            else:
                self.demo_stats['performance_grade'] = "🔴 Scarso"
                
            time.sleep(1)  # Update ogni secondo

class DemoConfig:
    """Configurazione demo"""
    
    def __init__(self):
        self.data = {
            'effects.blur_intensity': 15,
            'effects.edge_smoothing': True,
            'effects.temporal_smoothing': True,
            'effects.noise_reduction': False,
            'ai.performance_mode': False,
            'gui.window_width': 600,
            'gui.window_height': 700,
            'gui.theme': 'clam'
        }
    
    def get(self, key, default=None):
        return self.data.get(key, default)
        
    def set(self, key, value):
        self.data[key] = value
        print(f"⚙️ [DEMO] Config {key} = {value}")
        
    def reset_to_defaults(self):
        print("🔄 [DEMO] Reset configurazione")

def main():
    """Entry point demo"""
    print("🎨 StreamBlur Pro - Modern UI Demo")
    print("=" * 50)
    print("Questa è una demo della nuova interfaccia moderna!")
    print("Tutte le funzioni sono simulate per mostrare il design.")
    print("=" * 50)
    print()
    
    try:
        # Crea app demo
        demo_app = DemoStreamBlurApp()
        
        # Importa e avvia UI moderna
        from src.gui.modern_control_panel import ModernStreamBlurPanel
        
        # Crea e avvia GUI
        gui = ModernStreamBlurPanel(demo_app)
        gui.run()
        
    except ImportError as e:
        print(f"❌ Errore import: {e}")
        print("Assicurati di essere nella directory corretta del progetto")
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
