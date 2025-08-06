#!/usr/bin/env python3
"""
StreamBlur Pro - Prototype v1
Primo prototipo funzionante con:
- Cattura webcam real-time
- Segmentazione AI MediaPipe 
- Blur sfondo regolabile
- Anteprima live

Ottimizzato per AMD RX 7900 XTX + Ryzen 9 5900X
"""

import cv2
import numpy as np
import mediapipe as mp
import time
from threading import Thread
import queue

class StreamBlurPro:
    def __init__(self):
        """Inizializza StreamBlur Pro"""
        print("🚀 Inizializzando StreamBlur Pro...")
        
        # Configurazione
        self.camera_width = 1280  # Risoluzione alta per sfruttare hardware
        self.camera_height = 720
        self.blur_intensity = 15   # Intensità blur (regolabile)
        self.running = False
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # Queue per threading
        self.frame_queue = queue.Queue(maxsize=2)
        
        # Inizializza componenti
        self._init_camera()
        self._init_ai()
        
        print("✅ StreamBlur Pro inizializzato!")
    
    def _init_camera(self):
        """Inizializza webcam con ottimizzazioni"""
        print("📹 Configurando webcam...")
        
        self.cap = cv2.VideoCapture(0)
        
        # Configurazione ottimale
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Riduce latenza
        
        # Verifica risoluzione effettiva
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"📐 Risoluzione: {actual_width}x{actual_height}")
        
        if not self.cap.isOpened():
            raise Exception("❌ Impossibile aprire la webcam!")
    
    def _init_ai(self):
        """Inizializza MediaPipe AI"""
        print("🤖 Caricando AI per segmentazione...")
        
        # Configura MediaPipe
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self.segmentation = self.mp_selfie_segmentation.SelfieSegmentation(
            model_selection=1  # Modello più accurato (0=veloce, 1=accurato)
        )
        
        print("✅ AI segmentazione caricata!")
    
    def _calculate_fps(self):
        """Calcola FPS real-time"""
        self.fps_counter += 1
        
        current_time = time.time()
        elapsed = current_time - self.fps_start_time
        
        if elapsed >= 1.0:  # Aggiorna FPS ogni secondo
            self.current_fps = self.fps_counter / elapsed
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def _apply_background_blur(self, frame, mask):
        """Applica blur professionale allo sfondo"""
        
        # Normalizza la mask (0-1 range)
        mask_normalized = mask.astype(np.float32)
        
        # Calcola kernel size (deve essere sempre dispari e > 0)
        kernel_size = max(3, self.blur_intensity * 2 + 1)  # Assicura sempre dispari
        if kernel_size % 2 == 0:  # Se pari, rendi dispari
            kernel_size += 1
        
        # Crea blur dello sfondo - doppio passaggio per qualità superiore
        blurred_background = cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
        
        # Secondo passaggio più leggero
        kernel_size_2 = max(3, self.blur_intensity + 2)
        if kernel_size_2 % 2 == 0:
            kernel_size_2 += 1
        blurred_background = cv2.GaussianBlur(blurred_background, (kernel_size_2, kernel_size_2), 0)
        
        # Espandi mask per 3 canali
        mask_3_channel = np.stack([mask_normalized] * 3, axis=-1)
        
        # Componi immagine finale: persona nitida + sfondo sfocato
        result = frame * mask_3_channel + blurred_background * (1 - mask_3_channel)
        
        return result.astype(np.uint8)
    
    def _add_performance_info(self, frame):
        """Aggiungi informazioni performance su frame"""
        
        # Info FPS
        fps_text = f"FPS: {self.current_fps:.1f}"
        cv2.putText(frame, fps_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Info blur intensity
        blur_text = f"Blur: {self.blur_intensity}"
        cv2.putText(frame, blur_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Watermark
        watermark = "StreamBlur Pro v1 - AMD Optimized"
        cv2.putText(frame, watermark, (10, frame.shape[0] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def _capture_thread(self):
        """Thread separato per cattura frame (ottimizzazione performance)"""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                # Aggiungi frame alla queue (non bloccante)
                if not self.frame_queue.full():
                    self.frame_queue.put(frame)
            time.sleep(0.001)  # Piccola pausa per non saturare CPU
    
    def process_frame(self, frame):
        """Processa singolo frame con AI e blur"""
        
        # Converti da BGR (OpenCV) a RGB (MediaPipe)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Segmentazione AI
        results = self.segmentation.process(rgb_frame)
        
        # Ottieni mask di segmentazione
        mask = results.segmentation_mask
        
        # Applica blur allo sfondo
        processed_frame = self._apply_background_blur(frame, mask)
        
        return processed_frame
    
    def run(self):
        """Avvia StreamBlur Pro con preview live"""
        print("\n🎬 Avviando StreamBlur Pro...")
        print("⚙️  Controlli:")
        print("   [+/-] Regola intensità blur")
        print("   [ESC] Esci")
        print("   [SPACE] Pausa/Resume")
        print("\n🎯 Premi un tasto per iniziare...")
        
        self.running = True
        
        # Avvia thread di cattura
        capture_thread = Thread(target=self._capture_thread, daemon=True)
        capture_thread.start()
        
        paused = False
        
        try:
            while True:
                # Gestione input utente
                key = cv2.waitKey(1) & 0xFF
                
                if key == 27:  # ESC per uscire
                    break
                elif key == ord(' '):  # SPACE per pausa
                    paused = not paused
                    print(f"⏸️  {'Pausa' if paused else 'Resume'}")
                elif key == ord('+') or key == ord('='):  # Aumenta blur
                    self.blur_intensity = min(25, self.blur_intensity + 2)
                    print(f"🔵 Blur aumentato: {self.blur_intensity}")
                elif key == ord('-'):  # Diminuisci blur
                    self.blur_intensity = max(3, self.blur_intensity - 2)
                    print(f"🔵 Blur diminuito: {self.blur_intensity}")
                
                if paused:
                    continue
                
                # Ottieni frame dalla queue
                if not self.frame_queue.empty():
                    frame = self.frame_queue.get()
                    
                    # Processa frame con AI
                    start_time = time.time()
                    processed_frame = self.process_frame(frame)
                    processing_time = time.time() - start_time
                    
                    # Aggiungi info performance
                    processed_frame = self._add_performance_info(processed_frame)
                    
                    # Mostra risultato
                    cv2.imshow('StreamBlur Pro - Live Preview', processed_frame)
                    
                    # Calcola FPS
                    self._calculate_fps()
                    
                    # Debug performance ogni 30 frame
                    if self.fps_counter % 30 == 0:
                        print(f"⚡ Performance: {processing_time*1000:.1f}ms/frame, {self.current_fps:.1f} FPS")
        
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
    """Entry point principale"""
    try:
        # Crea e avvia StreamBlur Pro
        stream_blur = StreamBlurPro()
        stream_blur.run()
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()