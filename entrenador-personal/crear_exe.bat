@echo off
REM Genera dist\EntrenadorPersonal.exe (un solo archivo, sin necesidad de Python instalado)
cd /d "%~dp0"
python -m pip install --upgrade pyinstaller pillow
python -m PyInstaller --noconfirm --onefile --windowed --name EntrenadorPersonal run.py
echo.
echo Listo: dist\EntrenadorPersonal.exe
pause
