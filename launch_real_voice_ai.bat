@echo off
echo 🎙️ REAL Voice AI Interview System Launcher
echo ==========================================
echo.

echo 📋 Starting components...
echo.

REM Check Python environment
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found
    pause
    exit /b 1
)
echo ✅ Python: Available

REM Start LiveKit server if not running
netstat -an | findstr :7880 > nul
if %errorlevel% neq 0 (
    echo 🚀 Starting LiveKit server...
    start /min cmd /c "livekit-server --dev --bind 0.0.0.0 --port 7880 --keys devkey:secret"
    timeout /t 5 /nobreak > nul
    echo ✅ LiveKit server: Started on port 7880
) else (
    echo ✅ LiveKit server: Already running
)

echo.
echo 🎯 REAL Voice AI System Ready!
echo.
echo 🔧 Components:
echo    📡 LiveKit Server: ws://localhost:7880
echo    🎙️ Voice AI Platform: http://localhost:8001
echo    🤖 Voice Agent: Embedded in platform
echo.
echo 🌐 Open your browser to: http://localhost:8001
echo.

echo 🚀 Starting Voice AI Platform...
python real_voice_ai_platform.py

pause
