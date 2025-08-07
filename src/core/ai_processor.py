# =============================================================================
# File 5: src/core/ai_processor.py
# =============================================================================

import cv2
import numpy as np
import mediapipe as mp
import time
from typing import Optional, Tuple
from collections import deque

from ..utils.config import StreamBlurConfig
from ..utils.performance import PerformanceMonitor

class AIProcessor:
    """Processore AI per segmentazione persona/sfondo"""
    
    def __init__(self, config: StreamBlurConfig, performance_monitor: PerformanceMonitor):
        self.config = config
        self.performance = performance_monitor
        
        # Configurazione AI
        self.ai_width = config.get('video.ai_width', 512)
        self.ai_height = config.get('video.ai_height', 288)
        self.model_selection = 1  # 0=veloce, 1=accurato
        
        # Feature toggles
        self.edge_smoothing = config.get('effects.edge_smoothing', True)
        self.temporal_smoothing = config.get('effects.temporal_smoothing', True)
        
        # Parametri ottimizzazione
        self.edge_kernel_size = config.get('performance.edge_kernel_size', 3)
        self.temporal_buffer_size = config.get('performance.temporal_buffer_size', 2)
        
        # MediaPipe
        self.mp_selfie_segmentation = None
        self.segmentation = None
        
        # Temporal smoothing buffer
        self.mask_buffer = deque(maxlen=self.temporal_buffer_size)
        
        # GPU acceleration (se disponibile)
        self.gpu_available = False
        
    def initialize(self) -> bool:
        """Inizializza processore AI"""
        print("🤖 Inizializzando AI processor...")
        
        try:
            # Inizializza MediaPipe
            self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
            self.segmentation = self.mp_selfie_segmentation.SelfieSegmentation(
                model_selection=self.model_selection
            )
            
            print(f"✅ AI inizializzato - Risoluzione: {self.ai_width}x{self.ai_height}")
            print(f"🎯 Modello: {'Accurato' if self.model_selection else 'Veloce'}")
            
            # Test GPU acceleration
            self._test_gpu_acceleration()
            
            return True
            
        except Exception as e:
            print(f"❌ Errore inizializzazione AI: {e}")
            return False
    
    def _test_gpu_acceleration(self):
        """Testa disponibilità GPU acceleration"""
        try:
            import pyopencl as cl
            platforms = cl.get_platforms()
            amd_platforms = [p for p in platforms if 'AMD' in p.name]
            
            if amd_platforms:
                print(f"🚀 GPU AMD rilevata: {amd_platforms[0].name}")
                self.gpu_available = True
            else:
                print("💻 Usando CPU per processing")
                
        except ImportError:
            print("💻 PyOpenCL non disponibile - usando CPU")
        except Exception as e:
            print(f"⚠️ Errore GPU detection: {e}")
    
    def process_frame(self, frame: np.ndarray, output_size: Tuple[int, int]) -> Optional[np.ndarray]:
        """Processa frame per segmentazione persona/sfondo"""
        start_time = time.time()
        
        try:
            # Ridimensiona per AI processing
            ai_frame = cv2.resize(frame, (self.ai_width, self.ai_height))
            
            # Converte BGR -> RGB per MediaPipe
            rgb_frame = cv2.cvtColor(ai_frame, cv2.COLOR_BGR2RGB)
            
            # Segmentazione AI
            results = self.segmentation.process(rgb_frame)
            mask = results.segmentation_mask
            
            if mask is None:
                return None
            
            # Ridimensiona mask alla risoluzione output
            mask_resized = cv2.resize(mask, output_size)
            mask_resized = (mask_resized * 255).astype(np.uint8)
            
            # Applica miglioramenti
            if self.edge_smoothing:
                mask_resized = self._apply_edge_smoothing(mask_resized)
            
            if self.temporal_smoothing:
                mask_resized = self._apply_temporal_smoothing(mask_resized)
            
            # Record performance
            processing_time = time.time() - start_time
            self.performance.record_processing_time(processing_time)
            
            return mask_resized
            
        except Exception as e:
            print(f"⚠️ Errore processing AI: {e}")
            return None
    
    def _apply_edge_smoothing(self, mask: np.ndarray) -> np.ndarray:
        """Applica edge smoothing per bordi più morbidi"""
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, 
                                         (self.edge_kernel_size, self.edge_kernel_size))
        
        # Morphological closing per riempire buchi
        mask_smooth = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Gaussian blur leggero per bordi smooth
        mask_smooth = cv2.GaussianBlur(mask_smooth, (3, 3), 0.5)
        
        return mask_smooth
    
    def _apply_temporal_smoothing(self, mask: np.ndarray) -> np.ndarray:
        """Applica temporal smoothing per stabilità movimento"""
        self.mask_buffer.append(mask.copy())
        
        if len(self.mask_buffer) >= 2:
            # Media ponderata: 70% frame corrente, 30% precedente
            smoothed_mask = (0.7 * mask.astype(np.float32) + 
                           0.3 * self.mask_buffer[-2].astype(np.float32))
            return smoothed_mask.astype(np.uint8)
        
        return mask
    
    def set_edge_smoothing(self, enabled: bool):
        """Abilita/disabilita edge smoothing"""
        self.edge_smoothing = enabled
        self.config.set('effects.edge_smoothing', enabled)
    
    def set_temporal_smoothing(self, enabled: bool):
        """Abilita/disabilita temporal smoothing"""
        self.temporal_smoothing = enabled
        if not enabled:
            self.mask_buffer.clear()
        self.config.set('effects.temporal_smoothing', enabled)
    
    def get_stats(self) -> dict:
        """Ottieni statistiche AI processor"""
        return {
            'ai_resolution': f"{self.ai_width}x{self.ai_height}",
            'model': 'Accurato' if self.model_selection else 'Veloce',
            'edge_smoothing': self.edge_smoothing,
            'temporal_smoothing': self.temporal_smoothing,
            'gpu_available': self.gpu_available,
            'buffer_size': len(self.mask_buffer)
        }
    
    def cleanup(self):
        """Pulizia risorse AI"""
        print("🧹 Cleanup AI processor...")
        
        if self.segmentation:
            self.segmentation.close()
            self.segmentation = None
        
        self.mask_buffer.clear()
        print("✅ AI cleanup completato")
