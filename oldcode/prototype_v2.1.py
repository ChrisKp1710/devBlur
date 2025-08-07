#!/usr/bin/env python3
"""
StreamBlur Pro - Prototype v2.1 - Performance Optimized
Versione ottimizzata che mantiene i miglioramenti ma con performance accettabili:
- Edge Smoothing ottimizzato (veloce)
- Temporal Smoothing leggero
- Noise Reduction opzionale e veloce
- Multi-resolution AI intelligente

Ottimizzato per AMD RX 7900 XTX + Ryzen 9 5900X
Target: 20+ FPS con miglioramenti attivi
"""

import cv2
import numpy as np
import mediapipe as mp
import time
from threading import Thread
import queue
from collections import deque

class StreamBlurProV21:
    def __init__(self):
        """Inizializza StreamBlur Pro v2.1 ottimizzato"""
        print("🚀 Inizializzando StreamBlur Pro v2.1 (Ottimizzato)...")
        
        # Configurazione bilanciata
        self.camera_width = 1280
        self.camera_height = 720
        self.ai_width = 512  # Bilanciato: qualità vs performance
        self.ai_height = 288
        self.blur_intensity = 15
        
        # Feature toggle ottimizzate
        self.edge_smoothing = True
        self.temporal_smoothing = True
        self.noise_reduction = False  # OFF di default (troppo pesante)
        self.running = False
        
        # Parametri ottimizzati
        self.edge_kernel_size = 3  # Più piccolo = più veloce
        self.temporal_buffer_size = 2  # Ridotto per performance
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # Threading e buffering
        self.frame_queue = queue.Queue(maxsize=2)
        self.mask_buffer = deque(maxlen=self.temporal_buffer_size)
        
        # Inizializza componenti
        self._init_camera()
        self._init_ai()
        
        print("✅ StreamBlur Pro v2.1 inizializzato!")
    
    def _init_camera(self):
        """Inizializza webcam"""
        print("📹 Configurando webcam (v2.1)...")
        
        self.cap = cv2.VideoCapture(0)
        
        # Configurazione ottimale
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"📐 Risoluzione camera: {actual_width}x{actual_height}")
        print(f"🤖 Risoluzione AI: {self.ai_width}x{self.ai_height} (ottimizzata)")
        
        if not self.cap.isOpened():
            raise Exception("❌ Impossibile aprire la webcam!")
    
    def _init_ai(self):
        """Inizializza MediaPipe AI"""
        print("🤖 Caricando AI per segmentazione (v2.1)...")
        
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self.segmentation = self.mp_selfie_segmentation.SelfieSegmentation(
            model_selection=1  # Modello accurato ma gestibile
        )
        
        print("✅ AI segmentazione v2.1 caricata!")
    
    def _calculate_fps(self):
        """Calcola FPS real-time"""
        self.fps_counter += 1
        
        current_time = time.time()
        elapsed = current_time - self.fps_start_time
        
        if elapsed >= 1.0:
            self.current_fps = self.fps_counter / elapsed
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def _apply_edge_smoothing_fast(self, mask):
        """Edge smoothing veloce e ottimizzato"""
        if not self.edge_smoothing:
            return mask
            
        # Versione ottimizzata: solo operazioni essenziali
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))  # Kernel piccolo
        
        # Solo closing per riempire buchi piccoli
        mask_smooth = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Gaussian blur molto leggero
        mask_smooth = cv2.GaussianBlur(mask_smooth, (3, 3), 0.5)
        
        return mask_smooth
    
    def _apply_temporal_smoothing_fast(self, mask):
        """Temporal smoothing veloce"""
        if not self.temporal_smoothing:
            return mask
            
        # Aggiungi mask corrente al buffer
        self.mask_buffer.append(mask.copy())
        
        if len(self.mask_buffer) < 2:
            return mask
        
        # Media semplice e veloce (solo 2 frame)
        if len(self.mask_buffer) == 2:
            # 70% frame corrente, 30% frame precedente
            smoothed_mask = (0.7 * mask.astype(np.float32) + 
                           0.3 * self.mask_buffer[-2].astype(np.float32))
            return smoothed_mask.astype(np.uint8)
        
        return mask
    
    def _apply_noise_reduction_fast(self, frame):
        """Noise reduction veloce (opzionale)"""
        if not self.noise_reduction:
            return frame
            
        # Versione veloce: bilateral filter invece di Non-local means
        return cv2.bilateralFilter(frame, 5, 50, 50)
    
    def _apply_background_blur_optimized(self, frame, mask):
        """Blur ottimizzato per performance"""
        
        # Normalizza la mask
        mask_normalized = mask.astype(np.float32) / 255.0
        
        # Calcola kernel size
        kernel_size = max(3, self.blur_intensity * 2 + 1)
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        # Blur a singolo passaggio (più veloce)
        blurred_background = cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
        
        # Effetto bokeh solo per blur molto intensi (>20)
        if self.blur_intensity > 20:
            # Bokeh semplificato
            kernel_size_bokeh = min(kernel_size, 15)  # Limita dimensione
            if kernel_size_bokeh % 2 == 0:
                kernel_size_bokeh += 1
            blurred_background = cv2.medianBlur(blurred_background, kernel_size_bokeh)
        
        # Espandi mask per 3 canali
        mask_3_channel = np.stack([mask_normalized] * 3, axis=-1)
        
        # Leggero blur della mask per transizioni smooth
        mask_blurred = cv2.GaussianBlur(mask_3_channel, (3, 3), 1)
        
        # Componi immagine finale
        result = frame * mask_blurred + blurred_background * (1 - mask_blurred)
        
        return result.astype(np.uint8)
    
    def _add_performance_info_optimized(self, frame):
        """Info performance ottimizzate"""
        
        # Background più piccolo
        overlay = frame.copy()
        cv2.rectangle(overlay, (5, 5), (280, 100), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.8, overlay, 0.2, 0)
        
        # Info FPS con colore dinamico
        fps_color = (0, 255, 0) if self.current_fps >= 20 else (0, 255, 255) if self.current_fps >= 15 else (0, 0, 255)
        cv2.putText(frame, f"FPS: {self.current_fps:.1f}", (10, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, fps_color, 2)
        
        # Info blur
        cv2.putText(frame, f"Blur: {self.blur_intensity}", (10, 45), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Features attive (compatto)
        features = []
        if self.edge_smoothing: features.append("E+")
        if self.temporal_smoothing: features.append("T+")
        if self.noise_reduction: features.append("N+")
        
        if features:
            cv2.putText(frame, " ".join(features), (10, 65), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        # Watermark
        cv2.putText(frame, "StreamBlur Pro v2.1 - Optimized", 
                   (10, frame.shape[0] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        return frame
    
    def _capture_thread(self):
        """Thread cattura frame"""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                if not self.frame_queue.full():
                    self.frame_queue.put(frame)
            time.sleep(0.001)
    
    def process_frame_optimized(self, frame):
        """Processing frame ottimizzato v2.1"""
        
        # Ridimensiona per AI (bilanciato)
        ai_frame = cv2.resize(frame, (self.ai_width, self.ai_height))
        
        # Converti a RGB
        rgb_frame = cv2.cvtColor(ai_frame, cv2.COLOR_BGR2RGB)
        
        # Segmentazione AI
        results = self.segmentation.process(rgb_frame)
        mask = results.segmentation_mask
        
        # Ridimensiona mask alla risoluzione originale
        mask_resized = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
        mask_resized = (mask_resized * 255).astype(np.uint8)
        
        # Applica miglioramenti ottimizzati
        mask_enhanced = self._apply_edge_smoothing_fast(mask_resized)
        mask_enhanced = self._apply_temporal_smoothing_fast(mask_enhanced)
        
        # Noise reduction opzionale (veloce)
        processed_frame = self._apply_noise_reduction_fast(frame)
        
        # Blur ottimizzato
        final_frame = self._apply_background_blur_optimized(processed_frame, mask_enhanced)
        
        return final_frame
    
    def run(self):
        """Avvia StreamBlur Pro v2.1"""
        print("\n🎬 Avviando StreamBlur Pro v2.1 (Ottimizzato)...")
        print("⚙️  Controlli:")
        print("   [+/-] Blur intensity")
        print("   [E] Edge Smoothing (veloce)")
        print("   [T] Temporal Smoothing (leggero)")
        print("   [N] Noise Reduction (opzionale - rallenta)")
        print("   [ESC] Esci, [SPACE] Pausa")
        print("\n🎯 Target: 20+ FPS con miglioramenti!")
        
        self.running = True
        
        capture_thread = Thread(target=self._capture_thread, daemon=True)
        capture_thread.start()
        
        paused = False
        
        try:
            while True:
                key = cv2.waitKey(1) & 0xFF
                
                if key == 27:  # ESC
                    break
                elif key == ord(' '):  # SPACE
                    paused = not paused
                    print(f"⏸️  {'Pausa' if paused else 'Resume'}")
                elif key == ord('+') or key == ord('='):
                    self.blur_intensity = min(25, self.blur_intensity + 2)
                    print(f"🔵 Blur: {self.blur_intensity}")
                elif key == ord('-'):
                    self.blur_intensity = max(3, self.blur_intensity - 2)
                    print(f"🔵 Blur: {self.blur_intensity}")
                elif key == ord('e') or key == ord('E'):
                    self.edge_smoothing = not self.edge_smoothing
                    print(f"🎯 Edge Smoothing: {'ON' if self.edge_smoothing else 'OFF'}")
                elif key == ord('t') or key == ord('T'):
                    self.temporal_smoothing = not self.temporal_smoothing
                    if not self.temporal_smoothing:
                        self.mask_buffer.clear()
                    print(f"⏱️  Temporal Smoothing: {'ON' if self.temporal_smoothing else 'OFF'}")
                elif key == ord('n') or key == ord('N'):
                    self.noise_reduction = not self.noise_reduction
                    print(f"🔧 Noise Reduction: {'ON (rallenta!)' if self.noise_reduction else 'OFF'}")
                
                if paused:
                    continue
                
                if not self.frame_queue.empty():
                    frame = self.frame_queue.get()
                    
                    start_time = time.time()
                    processed_frame = self.process_frame_optimized(frame)
                    processing_time = time.time() - start_time
                    
                    processed_frame = self._add_performance_info_optimized(processed_frame)
                    
                    cv2.imshow('StreamBlur Pro v2.1 - Performance Optimized', processed_frame)
                    
                    self._calculate_fps()
                    
                    # Debug meno frequente
                    if self.fps_counter % 90 == 0:
                        print(f"⚡ v2.1 Performance: {processing_time*1000:.1f}ms, {self.current_fps:.1f} FPS")
        
        except KeyboardInterrupt:
            print("\n⏹️  Interruzione utente")
        
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Pulizia risorse"""
        print("🧹 Pulizia risorse...")
        self.running = False
        
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        
        cv2.destroyAllWindows()
        print("✅ Cleanup completato!")

def main():
    """Entry point v2.1"""
    try:
        print("🚀 StreamBlur Pro v2.1 - Performance Optimized Edition")
        print("🎯 Bilanciamento: Qualità migliorata + Performance accettabili")
        print()
        
        stream_blur = StreamBlurProV21()
        stream_blur.run()
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()