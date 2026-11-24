@echo off
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
 echo Python 3 tidak ditemukan. Install Python 3.10+ dan aktifkan Add Python to PATH.
 pause
 exit /b 1
)
if not exist data mkdir data
start "NUMERA Server" /D "%~dp0" cmd /k python server.py
timeout /t 2 >nul
start http://127.0.0.1:8000
echo NUMERA sedang dijalankan di http://127.0.0.1:8000
