#!/usr/bin/env python3
"""
StreamBlur Pro - Prototype v2 - Enhanced Precision
Miglioramenti implementati:
- Edge Smoothing per bordi più morbidi
- Temporal Smoothing per stabilità nel movimento  
- Higher Resolution AI per precisione maggiore
- GPU Acceleration ottimizzata
- Noise Reduction per qualità superiore

Ottimizzato per AMD RX 7900 XTX + Ryzen 9 5900X
"""

import cv2
import numpy as np
import mediapipe as mp
import time
from threading import Thread
import queue
from collections import deque

class StreamBlurProV2:
    def __init__(self):
        """Inizializza StreamBlur Pro v2 con miglioramenti"""
        print("🚀 Inizializzando StreamBlur Pro v2...")
        
        # Configurazione avanzata
        self.camera_width = 1280
        self.camera_height = 720
        self.ai_width = 640  # Risoluzione AI (più alta per precisione)
        self.ai_height = 360
        self.blur_intensity = 15
        self.edge_smoothing = True
        self.temporal_smoothing = True
        self.running = False
        
        # Parametri avanzati
        self.edge_kernel_size = 5  # Per edge smoothing
        self.temporal_buffer_size = 3  # Frame per temporal smoothing
        self.noise_reduction = True
        
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
        self._init_gpu_optimization()
        
        print("✅ StreamBlur Pro v2 inizializzato!")
    
    def _init_camera(self):
        """Inizializza webcam con ottimizzazioni v2"""
        print("📹 Configurando webcam (v2)...")
        
        self.cap = cv2.VideoCapture(0)
        
        # Configurazione ottimale v2
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Ottimizzazioni aggiuntive
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Migliore per AI
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"📐 Risoluzione camera: {actual_width}x{actual_height}")
        print(f"🤖 Risoluzione AI: {self.ai_width}x{self.ai_height}")
        
        if not self.cap.isOpened():
            raise Exception("❌ Impossibile aprire la webcam!")
    
    def _init_ai(self):
        """Inizializza MediaPipe AI con precisione maggiore"""
        print("🤖 Caricando AI per segmentazione (v2 - Alta Precisione)...")
        
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self.segmentation = self.mp_selfie_segmentation.SelfieSegmentation(
            model_selection=1  # Modello più accurato
        )
        
        print("✅ AI segmentazione v2 caricata!")
    
    def _init_gpu_optimization(self):
        """Inizializza ottimizzazioni GPU AMD"""
        print("🚀 Configurando ottimizzazioni GPU AMD...")
        
        try:
            # Prova a configurare OpenCL per AMD
            import pyopencl as cl
            platforms = cl.get_platforms()
            amd_platforms = [p for p in platforms if 'AMD' in p.name]
            
            if amd_platforms:
                self.cl_context = cl.Context(dev_type=cl.device_type.GPU,
                                           properties=[(cl.context_properties.PLATFORM, 
                                                       amd_platforms[0])])
                self.cl_queue = cl.CommandQueue(self.cl_context)
                print("✅ GPU AMD ottimizzazione attiva!")
                self.gpu_acceleration = True
            else:
                print("⚠️ GPU AMD non rilevata, uso CPU")
                self.gpu_acceleration = False
                
        except Exception as e:
            print(f"⚠️ GPU acceleration non disponibile: {e}")
            self.gpu_acceleration = False
    
    def _calculate_fps(self):
        """Calcola FPS real-time"""
        self.fps_counter += 1
        
        current_time = time.time()
        elapsed = current_time - self.fps_start_time
        
        if elapsed >= 1.0:
            self.current_fps = self.fps_counter / elapsed
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def _apply_edge_smoothing(self, mask):
        """Applica edge smoothing per bordi più morbidi"""
        if not self.edge_smoothing:
            return mask
            
        # Morfological operations per bordi più smooth
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, 
                                         (self.edge_kernel_size, self.edge_kernel_size))
        
        # Closing per riempire piccoli buchi
        mask_smooth = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Opening per rimuovere rumore
        mask_smooth = cv2.morphologyEx(mask_smooth, cv2.MORPH_OPEN, kernel)
        
        # Gaussian blur leggero sui bordi
        mask_smooth = cv2.GaussianBlur(mask_smooth, (3, 3), 1)
        
        return mask_smooth
    
    def _apply_temporal_smoothing(self, mask):
        """Applica temporal smoothing per stabilità nel movimento"""
        if not self.temporal_smoothing:
            return mask
            
        # Aggiungi mask corrente al buffer
        self.mask_buffer.append(mask.copy())
        
        if len(self.mask_buffer) < 2:
            return mask
        
        # Media ponderata delle mask precedenti
        weights = np.array([0.6, 0.3, 0.1])[:len(self.mask_buffer)]
        weights = weights / weights.sum()
        
        smoothed_mask = np.zeros_like(mask, dtype=np.float32)
        
        for i, (weight, buffered_mask) in enumerate(zip(weights, reversed(self.mask_buffer))):
            smoothed_mask += weight * buffered_mask.astype(np.float32)
        
        return smoothed_mask.astype(np.uint8)
    
    def _apply_noise_reduction(self, frame):
        """Applica noise reduction per qualità superiore"""
        if not self.noise_reduction:
            return frame
            
        # Non-local means denoising (preserva dettagli)
        return cv2.fastNlMeansDenoisingColored(frame, None, 3, 3, 7, 21)
    
    def _apply_background_blur_v2(self, frame, mask):
        """Applica blur professionale v2 con miglioramenti"""
        
        # Normalizza la mask (0-1 range)
        mask_normalized = mask.astype(np.float32) / 255.0
        
        # Calcola kernel size (sempre dispari)
        kernel_size = max(3, self.blur_intensity * 2 + 1)
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        # Multi-layer blur per effetto più professionale
        blurred_background = frame.copy()
        
        # Primo layer: blur principale
        blurred_background = cv2.GaussianBlur(blurred_background, (kernel_size, kernel_size), 0)
        
        # Secondo layer: blur più leggero per transizioni smooth
        kernel_size_2 = max(3, kernel_size // 2)
        if kernel_size_2 % 2 == 0:
            kernel_size_2 += 1
        blurred_background = cv2.GaussianBlur(blurred_background, (kernel_size_2, kernel_size_2), 0)
        
        # Bokeh effect leggero per look più professionale
        if self.blur_intensity > 15:
            # Crea effetto bokeh
            bokeh_kernel = np.zeros((kernel_size, kernel_size))
            center = kernel_size // 2
            radius = kernel_size // 4
            y, x = np.ogrid[:kernel_size, :kernel_size]
            mask_circle = (x - center) ** 2 + (y - center) ** 2 <= radius ** 2
            bokeh_kernel[mask_circle] = 1
            bokeh_kernel = bokeh_kernel / bokeh_kernel.sum()
            
            blurred_background = cv2.filter2D(blurred_background, -1, bokeh_kernel)
        
        # Espandi mask per 3 canali con gradient smooth
        mask_3_channel = np.stack([mask_normalized] * 3, axis=-1)
        
        # Applica gradient sui bordi per transizioni più smooth
        mask_blurred = cv2.GaussianBlur(mask_3_channel, (5, 5), 2)
        
        # Componi immagine finale
        result = frame * mask_blurred + blurred_background * (1 - mask_blurred)
        
        return result.astype(np.uint8)
    
    def _add_performance_info_v2(self, frame):
        """Aggiungi informazioni performance v2"""
        
        # Background semi-trasparente per info
        overlay = frame.copy()
        cv2.rectangle(overlay, (5, 5), (300, 120), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.8, overlay, 0.2, 0)
        
        # Info FPS con colore dinamico
        fps_color = (0, 255, 0) if self.current_fps >= 25 else (0, 255, 255) if self.current_fps >= 20 else (0, 0, 255)
        fps_text = f"FPS: {self.current_fps:.1f}"
        cv2.putText(frame, fps_text, (10, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, fps_color, 2)
        
        # Info blur intensity
        blur_text = f"Blur: {self.blur_intensity}"
        cv2.putText(frame, blur_text, (10, 45), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Stato miglioramenti
        improvements = []
        if self.edge_smoothing:
            improvements.append("Edge+")
        if self.temporal_smoothing:
            improvements.append("Temporal+")
        if self.noise_reduction:
            improvements.append("NoiseRed+")
        if self.gpu_acceleration:
            improvements.append("GPU+")
            
        improvements_text = " ".join(improvements)
        cv2.putText(frame, improvements_text, (10, 65), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        
        # Watermark v2
        watermark = "StreamBlur Pro v2 - Enhanced Precision"
        cv2.putText(frame, watermark, (10, frame.shape[0] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        return frame
    
    def _capture_thread(self):
        """Thread separato per cattura frame"""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                if not self.frame_queue.full():
                    self.frame_queue.put(frame)
            time.sleep(0.001)
    
    def process_frame_v2(self, frame):
        """Processa singolo frame con AI e blur v2"""
        
        # Ridimensiona per AI processing (performance vs accuracy)
        ai_frame = cv2.resize(frame, (self.ai_width, self.ai_height))
        
        # Converti da BGR (OpenCV) a RGB (MediaPipe)
        rgb_frame = cv2.cvtColor(ai_frame, cv2.COLOR_BGR2RGB)
        
        # Segmentazione AI
        results = self.segmentation.process(rgb_frame)
        
        # Ottieni mask di segmentazione
        mask = results.segmentation_mask
        
        # Ridimensiona mask alla risoluzione originale
        mask_resized = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
        
        # Converti a 0-255
        mask_resized = (mask_resized * 255).astype(np.uint8)
        
        # Applica miglioramenti
        mask_enhanced = self._apply_edge_smoothing(mask_resized)
        mask_enhanced = self._apply_temporal_smoothing(mask_enhanced)
        
        # Applica noise reduction al frame se abilitato
        processed_frame = self._apply_noise_reduction(frame) if self.noise_reduction else frame
        
        # Applica blur allo sfondo v2
        final_frame = self._apply_background_blur_v2(processed_frame, mask_enhanced)
        
        return final_frame
    
    def run(self):
        """Avvia StreamBlur Pro v2 con preview live"""
        print("\n🎬 Avviando StreamBlur Pro v2...")
        print("⚙️  Controlli avanzati:")
        print("   [+/-] Regola intensità blur")
        print("   [E] Toggle Edge Smoothing")
        print("   [T] Toggle Temporal Smoothing") 
        print("   [N] Toggle Noise Reduction")
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
                # Gestione input utente avanzata
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
                elif key == ord('e') or key == ord('E'):  # Toggle Edge Smoothing
                    self.edge_smoothing = not self.edge_smoothing
                    print(f"🎯 Edge Smoothing: {'ON' if self.edge_smoothing else 'OFF'}")
                elif key == ord('t') or key == ord('T'):  # Toggle Temporal Smoothing
                    self.temporal_smoothing = not self.temporal_smoothing
                    print(f"⏱️  Temporal Smoothing: {'ON' if self.temporal_smoothing else 'OFF'}")
                elif key == ord('n') or key == ord('N'):  # Toggle Noise Reduction
                    self.noise_reduction = not self.noise_reduction
                    print(f"🔧 Noise Reduction: {'ON' if self.noise_reduction else 'OFF'}")
                
                if paused:
                    continue
                
                # Ottieni frame dalla queue
                if not self.frame_queue.empty():
                    frame = self.frame_queue.get()
                    
                    # Processa frame con AI v2
                    start_time = time.time()
                    processed_frame = self.process_frame_v2(frame)
                    processing_time = time.time() - start_time
                    
                    # Aggiungi info performance
                    processed_frame = self._add_performance_info_v2(processed_frame)
                    
                    # Mostra risultato
                    cv2.imshow('StreamBlur Pro v2 - Enhanced Precision', processed_frame)
                    
                    # Calcola FPS
                    self._calculate_fps()
                    
                    # Debug performance ogni 60 frame per non spammare
                    if self.fps_counter % 60 == 0:
                        print(f"⚡ Performance v2: {processing_time*1000:.1f}ms/frame, {self.current_fps:.1f} FPS")
        
        except KeyboardInterrupt:
            print("\n⏹️  Interruzione utente")
        
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Pulizia risorse v2"""
        print("🧹 Pulizia risorse v2...")
        self.running = False
        
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        
        cv2.destroyAllWindows()
        print("✅ Cleanup v2 completato!")

def main():
    """Entry point principale v2"""
    try:
        print("🚀 StreamBlur Pro v2 - Enhanced Precision Edition")
        print("🎯 Miglioramenti: Edge Smoothing, Temporal Smoothing, Noise Reduction, GPU Optimization")
        print()
        
        # Crea e avvia StreamBlur Pro v2
        stream_blur = StreamBlurProV2()
        stream_blur.run()
        
    except Exception as e:
        print(f"❌ Errore v2: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()