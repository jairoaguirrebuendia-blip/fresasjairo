@echo off
REM Inicia Entrenador Personal (requiere Python 3.9+ de python.org con tkinter)
cd /d "%~dp0"
where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw run.py
) else (
    python run.py
)
