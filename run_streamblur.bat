@echo off
REM ===============================================
REM StreamBlur Pro v4.0 - Launcher per Windows
REM ===============================================

echo 🎥 Avvio StreamBlur Pro v4.0...
echo.

cd /d "%~dp0"

REM Controlla se l'ambiente virtuale esiste
if not exist "streamblur_env\Scripts\python.exe" (
    echo ❌ Ambiente virtuale non trovato!
    echo Assicurati che streamblur_env sia presente
    pause
    exit /b 1
)

REM Esegui StreamBlur Pro
streamblur_env\Scripts\python.exe -m src.main

echo.
echo 👋 StreamBlur Pro terminato!
pause
