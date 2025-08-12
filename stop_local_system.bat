@echo off
cls
echo.
echo ================================================================
echo                🛑 STOPPING LOCAL AI INTERVIEW SYSTEM  
echo ================================================================
echo.

echo 🐳 Stopping LiveKit Server...
docker-compose down 2>nul
if not errorlevel 1 (
    echo ✅ LiveKit server stopped
) else (
    echo ℹ️  LiveKit server was not running
)

echo 🤖 Stopping AI Agent processes...
taskkill /F /FI "WINDOWTITLE eq AI Interview Agent*" 2>nul
if not errorlevel 1 (
    echo ✅ AI Agent stopped
) else (
    echo ℹ️  AI Agent was not running
)

echo 🌐 Stopping Web Server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080') do (
    taskkill /F /PID %%a 2>nul
)
echo ✅ Web server stopped

echo 🧹 Cleaning up...
echo ✅ Cleanup complete

echo.
echo 🏁 SYSTEM SHUTDOWN COMPLETE!
echo ================================================================
echo.
echo All local AI interview system components have been stopped.
echo You can now:
echo   - Start the system again with: start_local_system.bat
echo   - Or run individual components manually
echo.
pause
