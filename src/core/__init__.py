# =============================================================================
# File 10: src/core/__init__.py
# =============================================================================

"""
StreamBlur Pro - Core Modules
Contiene i moduli principali per l'elaborazione video
"""

from .camera import CameraManager
from .ai_processor import AIProcessor
from .effects import EffectsProcessor
from .virtual_camera import VirtualCameraManager

__all__ = [
    'CameraManager',
    'AIProcessor', 
    'EffectsProcessor',
    'VirtualCameraManager'
]