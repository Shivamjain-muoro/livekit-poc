@echo off
cls
echo.
echo ================================================================
echo           🚀 SIMPLIFIED AI INTERVIEW SYSTEM STARTUP
echo ================================================================
echo.

echo 🔧 Step 1: Starting LiveKit Server...
echo ================================================================
docker-compose down >nul 2>&1
echo 📦 Starting LiveKit container...
docker-compose up livekit -d

if errorlevel 1 (
    echo ❌ Failed to start LiveKit server
    pause
    exit /b 1
)

echo ✅ LiveKit server started successfully
echo 🔗 Server URL: ws://localhost:7880
echo.

echo ⏳ Waiting for LiveKit server to initialize...
timeout /t 5 /nobreak >nul

echo.
echo ✅ LIVEKIT SERVER READY!
echo ================================================================
echo.
echo 📋 SYSTEM STATUS:
echo    🔧 LiveKit Server:   ws://localhost:7880 ✅ RUNNING
echo    🌐 Your Frontend:    http://localhost:3000 (external)
echo.
echo 🤖 NEXT STEP: Start AI Agent
echo    Run: python complete_interview_agent.py
echo.
echo 📊 TO CHECK LIVEKIT STATUS:
echo    - Docker logs: docker logs livekit-poc-livekit-1
echo    - Container status: docker ps
echo.
echo 🛑 TO STOP LIVEKIT:
echo    - Run: stop_local_system.bat
echo    - Or: docker-compose down
echo.
echo Press any key to continue...
pause >nul

echo.
echo 🤖 Starting AI Agent...
echo ================================================================
python complete_interview_agent.py
