@echo off
echo Starting LiveKit Interview System...
echo ====================================

echo Starting LiveKit server...
cd docker
docker-compose up -d
cd ..

echo Waiting for LiveKit server...
timeout /t 5 /nobreak > nul

echo Starting interview agent...
echo Press Ctrl+C to stop
echo Run generate_web_url.py in another terminal
echo.

python core/pure_livekit_interview_agent.py dev
