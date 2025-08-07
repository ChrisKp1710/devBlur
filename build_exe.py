#!/usr/bin/env python3
# =============================================================================
# Build Script per StreamBlur Pro Executable
# =============================================================================

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_executable():
    """Crea eseguibile StreamBlur Pro"""
    print("🔨 Building StreamBlur Pro Executable...")
    
    # Directory base
    base_dir = Path(__file__).parent
    src_dir = base_dir / "src"
    dist_dir = base_dir / "dist"
    build_dir = base_dir / "build"
    
    # Pulisci directory precedenti
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Comando PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",                    # Singolo eseguibile
        "--windowed",                   # Senza console (per GUI)
        "--name=StreamBlurPro",         # Nome eseguibile
        "--icon=icon.ico",              # Icona (se esiste)
        "--add-data=src;src",           # Includi cartella src
        "--hidden-import=mediapipe",    # Import nascosti
        "--hidden-import=cv2",
        "--hidden-import=numpy",
        "--hidden-import=pyvirtualcam",
        "--hidden-import=tkinter",
        "--collect-all=mediapipe",      # Tutti i file MediaPipe
        str(src_dir / "main.py")        # File principale
    ]
    
    # Rimuovi icona se non esiste
    icon_path = base_dir / "icon.ico"
    if not icon_path.exists():
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
    
    print(f"🚀 Eseguendo: {' '.join(cmd)}")
    
    try:
        # Esegui PyInstaller
        result = subprocess.run(cmd, cwd=base_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build completato con successo!")
            
            # Verifica eseguibile
            exe_path = dist_dir / "StreamBlurPro.exe"
            if exe_path.exists():
                print(f"🎯 Eseguibile creato: {exe_path}")
                print(f"📦 Dimensione: {exe_path.stat().st_size / (1024*1024):.1f} MB")
                return True
            else:
                print("❌ Eseguibile non trovato!")
                return False
        else:
            print("❌ Errore durante build:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Errore build: {e}")
        return False

def create_launcher_script():
    """Crea script launcher semplice"""
    launcher_content = '''@echo off
title StreamBlur Pro Launcher
echo.
echo ============================================================
echo 🎥 StreamBlur Pro v4.0 - Modular Edition
echo 🎯 Open Source Alternative to NVIDIA Broadcast for AMD
echo ⚡ Optimized for AMD RX 7900 XTX + Ryzen 9 5900X
echo ============================================================
echo.
echo 🚀 Avviando StreamBlur Pro...
echo.

cd /d "%~dp0"
streamblur_env\\Scripts\\python.exe -m src.main --gui

echo.
echo 📊 StreamBlur Pro terminato.
pause
'''
    
    launcher_path = Path(__file__).parent / "StreamBlurPro_Launcher.bat"
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print(f"✅ Launcher script creato: {launcher_path}")

if __name__ == "__main__":
    print("🎯 StreamBlur Pro Build System")
    print("=" * 50)
    
    choice = input("\n1️⃣ Build Executable (.exe)\n2️⃣ Create Launcher Script (.bat)\n3️⃣ Entrambi\n\nScegli opzione (1/2/3): ")
    
    if choice in ["1", "3"]:
        print("\n🔨 Building executable...")
        success = build_executable()
        if not success:
            print("❌ Build fallito!")
            sys.exit(1)
    
    if choice in ["2", "3"]:
        print("\n📝 Creating launcher script...")
        create_launcher_script()
    
    print("\n✅ Build completato!")
    print("\n🎯 Come usare:")
    if choice in ["1", "3"]:
        print("   - Eseguibile: dist/StreamBlurPro.exe")
    if choice in ["2", "3"]:
        print("   - Launcher: StreamBlurPro_Launcher.bat")
