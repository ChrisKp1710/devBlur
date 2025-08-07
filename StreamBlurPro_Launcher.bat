@echo off
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
streamblur_env\Scripts\python.exe -m src.main --gui

echo.
echo 📊 StreamBlur Pro terminato.
pause
