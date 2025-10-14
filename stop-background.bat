@echo off
REM Stop Chatify Chatbot background process
echo Stopping Chatify Chatbot backend...

REM Kill all Python processes running start_simple.py
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq pythonw.exe" /FI "WINDOWTITLE eq Chatify-Backend*" /NH') do (
    taskkill /PID %%i /F >nul 2>&1
)

REM Also try to kill by port
for /f "tokens=5" %%i in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /PID %%i /F >nul 2>&1
)

echo Backend stopped.
pause


