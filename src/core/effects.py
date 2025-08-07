# =============================================================================
# File 6: src/core/effects.py
# =============================================================================

import cv2
import numpy as np
from typing import Optional, Tuple
from ..utils.config import StreamBlurConfig

class EffectsProcessor:
    """Processore effetti per StreamBlur Pro"""
    
    def __init__(self, config: StreamBlurConfig):
        self.config = config
        
        # Configurazione effetti con conversione sicura
        blur_intensity = config.get('effects.blur_intensity', 15)
        self.blur_intensity = blur_intensity if isinstance(blur_intensity, int) else 15
        
        noise_reduction = config.get('effects.noise_reduction', False)
        self.noise_reduction = noise_reduction if isinstance(noise_reduction, bool) else False
        
    def apply_background_blur(self, frame: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Applica blur professionale allo sfondo - versione ottimizzata"""
        
        # Normalizza mask (0-1 range)
        mask_normalized = mask.astype(np.float32) / 255.0
        
        # Calcola kernel size ottimizzato per performance
        # Riduciamo la formula per blur più leggero
        kernel_size = max(3, int(self.blur_intensity * 1.5) + 1)
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        # Blur più efficiente - un solo passaggio per blur leggeri
        if self.blur_intensity <= 15:
            # Blur leggero - un passaggio
            blurred_bg = cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
        else:
            # Blur intenso - doppio passaggio per qualità migliore
            blurred_bg = cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
            if self.blur_intensity > 20:
                kernel_size_bokeh = min(kernel_size, 13)  # Riduciamo da 15 a 13
                if kernel_size_bokeh % 2 == 0:
                    kernel_size_bokeh += 1
                blurred_bg = cv2.medianBlur(blurred_bg, kernel_size_bokeh)
        
        # Mask a 3 canali con blur per transizioni smooth
        mask_3ch = np.stack([mask_normalized] * 3, axis=-1)
        mask_blurred = cv2.GaussianBlur(mask_3ch, (3, 3), 1)
        
        # Componi risultato finale
        result = frame * mask_blurred + blurred_bg * (1 - mask_blurred)
        return result.astype(np.uint8)
    
    def apply_noise_reduction(self, frame: np.ndarray) -> np.ndarray:
        """Applica riduzione rumore (opzionale)"""
        if not self.noise_reduction:
            return frame
            
        # Bilateral filter per riduzione rumore veloce
        return cv2.bilateralFilter(frame, 5, 50, 50)
    
    def set_blur_intensity(self, intensity: int):
        """Imposta intensità blur"""
        self.blur_intensity = max(1, min(25, intensity))
        self.config.set('effects.blur_intensity', intensity)
    
    def set_noise_reduction(self, enabled: bool):
        """Abilita/disabilita noise reduction"""
        self.noise_reduction = enabled
        self.config.set('effects.noise_reduction', enabled)
    
    def get_stats(self) -> dict:
        """Ottieni statistiche effetti"""
        return {
            'blur_intensity': self.blur_intensity,
            'noise_reduction': self.noise_reduction
        }
