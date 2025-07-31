@echo off
echo 🎙️ Starting Real-Time Voice AI Interview System
echo ================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

echo ✅ Python is available
echo.

REM Install dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements_voice_ai.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed
echo.

REM Check LiveKit server
echo 🔍 Checking LiveKit server status...
curl -s http://localhost:7880 >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ LiveKit server not running on localhost:7880
    echo 💡 Start LiveKit server first using: start_livekit_npm.bat
    echo.
    set /p choice="Continue without LiveKit server? (y/n): "
    if /i "%choice%" neq "y" (
        pause
        exit /b 1
    )
)

echo.
echo 🚀 Starting Voice AI Interview Backend...
echo.
echo 🌐 Web Interface: http://localhost:8001/voice-ai
echo 📊 Health Check: http://localhost:8001/health
echo 📚 API Docs: http://localhost:8001/docs
echo.
echo 💡 Instructions:
echo 1. Open http://localhost:8001/voice-ai in your browser
echo 2. Fill out the candidate form
echo 3. Click "Start Voice Interview"
echo 4. Speak naturally - no buttons needed during interview!
echo.

python realtime_ai_interview_agent.py

echo.
echo 🛑 Voice AI Interview System stopped
pause
