@echo off
echo 🚀 Starting LiveKit Server (No Docker Required)...
echo.

REM Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Installing LiveKit server via npm requires Node.js.
    echo.
    echo 💡 Alternative: Download binary from GitHub:
    echo    https://github.com/livekit/livekit-server/releases
    echo.
    pause
    exit /b 1
)

echo ✅ Node.js is available
echo.

REM Check if LiveKit server is already installed
livekit-server --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing LiveKit server via npm...
    npm install -g @livekit/livekit-server
    if %errorlevel% neq 0 (
        echo ❌ Failed to install LiveKit server
        echo Try running as Administrator or install manually
        pause
        exit /b 1
    )
)

echo ✅ LiveKit server is available
echo.

echo 🌐 Starting LiveKit server in development mode...
echo.
echo 🔧 Configuration:
echo    Port: 7880
echo    API Key: devkey
echo    API Secret: secret
echo    Development Mode: Enabled
echo.

REM Start the server
livekit-server --dev --bind 0.0.0.0 --port 7880 --keys devkey:secret

echo.
echo 🛑 LiveKit server stopped
pause
