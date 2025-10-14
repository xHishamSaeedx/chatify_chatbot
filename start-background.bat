@echo off
REM Start Chatify Chatbot in background (no console window)
echo Starting Chatify Chatbot backend in background...

REM Check if already running
tasklist /FI "WINDOWTITLE eq Chatify-Backend*" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Backend is already running!
    pause
    exit /b
)

REM Start in background using pythonw (no console window)
start "Chatify-Backend" /B pythonw start_simple.py

REM Wait a moment for startup
timeout /t 3 /nobreak >nul

REM Check if it started successfully
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing -TimeoutSec 2 | Out-Null; Write-Host 'Backend started successfully at http://localhost:8000' -ForegroundColor Green } catch { Write-Host 'Failed to start backend' -ForegroundColor Red }"

echo.
echo To stop the backend, run: stop-background.bat
pause


