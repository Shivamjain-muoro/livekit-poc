@echo off
echo 🚀 Starting Local LiveKit Server...
echo.

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo ✅ Docker is running
echo.

@echo off
echo � Starting Local LiveKit Server...
echo.

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo ✅ Docker is running
echo.

REM Stop any existing containers
echo 🧹 Cleaning up existing containers...
docker-compose down >nul 2>&1
docker-compose -f docker-compose-simple.yml down >nul 2>&1

echo 📋 Starting LiveKit server (simple configuration)...
docker-compose -f docker-compose-simple.yml up -d

if %errorlevel% equ 0 (
    echo.
    echo ✅ LiveKit server started successfully!
    echo.
    echo 🌐 LiveKit Server: ws://localhost:7880
    echo 🔑 API Key: devkey
    echo 🔐 API Secret: secret
    echo.
    echo 📱 You can now start your interview app:
    echo    python enhanced_backend.py
    echo.
    echo 🌍 Then open: http://localhost:8002/live-local
    echo.
    echo 📊 To check status: docker-compose -f docker-compose-simple.yml ps
    echo 📋 To view logs: docker-compose -f docker-compose-simple.yml logs livekit-simple
    echo � To stop: docker-compose -f docker-compose-simple.yml down
) else (
    echo ❌ Simple configuration failed, trying with config file...
    docker-compose up -d
    
    if %errorlevel% equ 0 (
        echo ✅ LiveKit server started with config file!
        echo �📊 To check status: docker-compose ps
        echo 📋 To view logs: docker-compose logs livekit
        echo 🛑 To stop: docker-compose down
    ) else (
        echo ❌ Failed to start LiveKit server
        echo Please check Docker Desktop and try again
        echo.
        echo 💡 Alternative: Try running without Docker:
        echo    npm install -g @livekit/livekit-server
        echo    livekit-server --dev --bind 0.0.0.0 --port 7880
    )
)

echo.
pause
