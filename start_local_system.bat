@echo off
cls
echo.
echo ================================================================
echo                🏠 LOCAL AI INTERVIEW SYSTEM STARTUP
echo ================================================================
echo.

echo 🔧 Setting up environment...
if not exist "config\.env" (
    echo ❌ Error: config\.env file not found
    echo Please ensure the environment configuration exists
    pause
    exit /b 1
)

echo ✅ Environment configuration found
echo.

echo 🐳 Step 1: Starting Local LiveKit Server...
echo ================================================================
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed or not running
    echo Please install Docker Desktop and start it
    echo Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo 📦 Pulling LiveKit server image (if needed)...
docker pull livekit/livekit-server:latest

echo 🚀 Starting LiveKit server container...
docker-compose down >nul 2>&1

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

echo 🤖 Step 2: Starting AI Interview Agent...
echo ================================================================
start "AI Interview Agent" cmd /k "cd /d %cd% && python complete_interview_agent.py"

echo ⏳ Waiting for agent to initialize...
timeout /t 3 /nobreak >nul

echo 🌐 Step 3: Starting Local Web Server...
echo ================================================================
start "Web Server" cmd /k "cd /d %cd%\web && python -m http.server 8080"

echo ⏳ Waiting for web server to start...
timeout /t 3 /nobreak >nul

echo 🎯 Step 4: Opening Interview Portal...
echo ================================================================
start "" "http://localhost:8080"

echo.
echo ✅ SYSTEM STARTUP COMPLETE!
echo ================================================================
echo.
echo 📋 SYSTEM INFORMATION:
echo    🏠 Interview Portal: http://localhost:8080
echo    🔧 LiveKit Server:   ws://localhost:7880  
echo    🤖 AI Agent:         Running in separate window
echo    🌐 Web Server:       http://localhost:8080
echo.
echo 📊 TO CHECK STATUS:
echo    - LiveKit:     docker logs livekit-local
echo    - Agent:       Check AI Interview Agent window
echo    - Web Server:  Check Web Server window
echo.
echo 🛑 TO STOP SYSTEM:
echo    - Run: stop_local_system.bat
echo    - Or manually close all windows and run: docker stop livekit-local
echo.
echo Press any key to continue (system will keep running)...
pause >nul
