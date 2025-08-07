@echo off
cd /d "%~dp0"
start "" streamblur_env\Scripts\python.exe -m src.main --gui
