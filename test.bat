@echo off
echo Testing LiveKit Interview System...
echo ===================================

echo 1. Checking dependencies...
python -c "import livekit, livekit.agents; print('LiveKit dependencies OK')"

echo 2. Checking environment...
python -c "import os; from dotenv import load_dotenv; load_dotenv('config/.env'); print('Google API key:', 'found' if os.getenv('GOOGLE_API_KEY') else 'missing')"

echo 3. Checking database...
python utils/check_database.py

echo 4. Running complete flow test...
python tests/test_complete_flow.py

echo.
echo Testing completed!
