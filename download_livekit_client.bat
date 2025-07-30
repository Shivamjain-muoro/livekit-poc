@echo off
echo 📥 Downloading LiveKit Client Library...
echo.

REM Create static directory if it doesn't exist
if not exist "static" mkdir static

echo Downloading LiveKit client library...
powershell -Command "Invoke-WebRequest -Uri 'https://unpkg.com/livekit-client@1.15.13/dist/livekit-client.umd.js' -OutFile 'static/livekit-client.js'"

if %errorlevel% equ 0 (
    echo ✅ LiveKit client library downloaded successfully!
    echo 📁 Saved to: static/livekit-client.js
    echo.
    echo You can now use the local LiveKit client in your HTML files.
) else (
    echo ❌ Failed to download LiveKit client library
    echo Please check your internet connection and try again
)

echo.
pause
