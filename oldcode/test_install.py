#!/usr/bin/env python3
"""
Test di installazione per StreamBlur Pro
Verifica che tutte le librerie funzionino correttamente
"""

def test_imports():
    """Test importazione librerie essenziali"""
    print("🔍 Testando importazioni...")
    
    try:
        import cv2
        print(f"✅ OpenCV: {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV: {e}")
        return False
    
    try:
        import mediapipe as mp
        print(f"✅ MediaPipe: {mp.__version__}")
    except ImportError as e:
        print(f"❌ MediaPipe: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✅ NumPy: {np.__version__}")
    except ImportError as e:
        print(f"❌ NumPy: {e}")
        return False
    
    try:
        from PIL import Image
        print(f"✅ Pillow: Installato")
    except ImportError as e:
        print(f"❌ Pillow: {e}")
        return False
    
    try:
        import pyvirtualcam
        print(f"✅ PyVirtualCam: Installato")
    except ImportError as e:
        print(f"❌ PyVirtualCam: {e}")
        return False
    
    try:
        import pyopencl as cl
        print(f"✅ PyOpenCL: Installato")
        
        # Test AMD GPU detection
        platforms = cl.get_platforms()
        amd_platforms = [p for p in platforms if 'AMD' in p.name]
        if amd_platforms:
            print(f"🚀 GPU AMD rilevata: {amd_platforms[0].name}")
        else:
            print("⚠️ Nessuna GPU AMD rilevata via OpenCL")
    except ImportError as e:
        print(f"⚠️ PyOpenCL: {e} (opzionale)")
    except Exception as e:
        print(f"⚠️ GPU AMD: {e} (opzionale)")
    
    return True

def test_camera():
    """Test webcam availability"""
    print("\n📹 Testando webcam...")
    
    import cv2
    
    # Prova ad aprire la webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Webcam non disponibile")
        return False
    
    # Leggi un frame
    ret, frame = cap.read()
    if not ret:
        print("❌ Impossibile leggere dalla webcam")
        cap.release()
        return False
    
    print(f"✅ Webcam OK - Risoluzione: {frame.shape[1]}x{frame.shape[0]}")
    cap.release()
    return True

def test_mediapipe():
    """Test MediaPipe segmentation"""
    print("\n🤖 Testando MediaPipe AI...")
    
    try:
        import mediapipe as mp
        
        # Inizializza il modello di segmentazione
        mp_selfie_segmentation = mp.solutions.selfie_segmentation
        segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)
        
        print("✅ MediaPipe Segmentation caricato")
        print("🎯 Modello: Selfie Segmentation (General)")
        
        # Test veloce con array dummy
        import numpy as np
        dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
        result = segmentation.process(dummy_image)
        
        if result.segmentation_mask is not None:
            print("✅ Test segmentazione riuscito")
        else:
            print("⚠️ Test segmentazione fallito")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore MediaPipe: {e}")
        return False

def test_system_info():
    """Mostra informazioni sistema"""
    print("\n💻 Informazioni Sistema:")
    
    import platform
    import sys
    
    print(f"🐍 Python: {sys.version}")
    print(f"💻 OS: {platform.system()} {platform.release()}")
    print(f"⚙️ Architettura: {platform.architecture()[0]}")
    
    try:
        import psutil
        print(f"💾 RAM: {psutil.virtual_memory().total // (1024**3)} GB")
        print(f"🔥 CPU: {psutil.cpu_count()} cores")
    except ImportError:
        print("📊 psutil non installato (opzionale)")

def main():
    """Esegui tutti i test"""
    print("🚀 StreamBlur Pro - Test Installazione\n")
    
    success = True
    
    # Informazioni sistema
    test_system_info()
    
    # Test importazioni
    if not test_imports():
        success = False
    
    # Test webcam
    if not test_camera():
        success = False
    
    # Test MediaPipe
    if not test_mediapipe():
        success = False
    
    print("\n" + "="*50)
    if success:
        print("🎉 TUTTI I TEST SUPERATI!")
        print("✅ L'ambiente è pronto per lo sviluppo!")
        print("🚀 Prossimo step: Primo prototipo funzionante!")
    else:
        print("❌ Alcuni test sono falliti.")
        print("🔧 Controlla i messaggi di errore sopra.")
    
    print("="*50)

if __name__ == "__main__":
    main()