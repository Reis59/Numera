@echo off
echo Menutup server NUMERA pada port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /PID %%a /T /F >nul 2>nul
echo Selesai.
pause
