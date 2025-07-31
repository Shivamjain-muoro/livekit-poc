@echo off
echo Starting Pure LiveKit Interview Agent
echo =====================================
echo.
echo This follows the exact pattern from Friday/Jarvis repo
echo Uses ONLY LiveKit Agents framework
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install requirements
echo Installing Pure LiveKit requirements...
pip install -r requirements_pure_livekit.txt

REM Check if .env exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Please copy env_template to .env and configure your API keys
    echo.
    pause
    exit /b 1
)

echo.
echo Starting Pure LiveKit Interview Agent...
echo Make sure your LiveKit server is running on port 7880
echo.

REM Run the pure LiveKit agent
python pure_livekit_interview_agent.py

pause
