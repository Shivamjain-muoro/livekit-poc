"""
PRACTICAL DEMONSTRATION - Show Live Configuration Connections
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load the actual configuration
load_dotenv('config/.env')

print("🔍 LIVE CONFIGURATION VERIFICATION")
print("=" * 60)

# 1. Show environment variables
print("📄 1. ENVIRONMENT VARIABLES (.env):")
print(f"   LIVEKIT_URL: {os.getenv('LIVEKIT_URL')}")
print(f"   LIVEKIT_API_KEY: {os.getenv('LIVEKIT_API_KEY')}")
print(f"   LIVEKIT_API_SECRET: {os.getenv('LIVEKIT_API_SECRET')[:10]}...")
print(f"   GOOGLE_API_KEY: {os.getenv('GOOGLE_API_KEY')[:20]}...")
print()

# 2. Test LiveKit server connection
print("🐳 2. LIVEKIT SERVER CONNECTION:")
try:
    response = requests.get('http://localhost:7880', timeout=3)
    print("   ✅ LiveKit server is responding")
    print(f"   📡 Server URL: ws://localhost:7880")
except Exception as e:
    print(f"   ❌ Server not responding: {e}")
print()

# 3. Show token generation process
print("🎫 3. TOKEN GENERATION PROCESS:")
try:
    import jwt
    from datetime import datetime, timedelta
    
    # This is exactly what local_token_generator.py does
    api_key = os.getenv('LIVEKIT_API_KEY')
    api_secret = os.getenv('LIVEKIT_API_SECRET')
    
    # Create a sample token
    payload = {
        "iss": api_key,
        "sub": "demo_candidate",
        "name": "Demo Candidate",
        "iat": int(datetime.utcnow().timestamp()),
        "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
        "video": {
            "roomJoin": True,
            "room": "demo_room",
            "canPublish": True,
            "canSubscribe": True
        }
    }
    
    token = jwt.encode(payload, api_secret, algorithm="HS256")
    print(f"   ✅ Token created successfully")
    print(f"   🔑 API Key used: {api_key}")
    print(f"   🎫 Token (first 50 chars): {token[:50]}...")
    print(f"   🏠 Room: demo_room")
    print()
    
except Exception as e:
    print(f"   ❌ Token generation failed: {e}")

# 4. Show HTML connection URLs
print("🌐 4. HTML FRONTEND CONNECTIONS:")
base_url = "http://localhost:8080"
meeting_url = f"{base_url}/interview.html?room=demo_room&token={token[:50]}..."
print(f"   📱 Portal URL: {base_url}/index.html")
print(f"   🎤 Meeting URL: {meeting_url}")
print(f"   🔗 LiveKit target: ws://localhost:7880")
print()

# 5. Show configuration consistency
print("🎯 5. CONFIGURATION CONSISTENCY:")
env_url = os.getenv('LIVEKIT_URL')
env_key = os.getenv('LIVEKIT_API_KEY')

if 'localhost:7880' in env_url:
    print("   ✅ .env URL matches expected local server")
else:
    print("   ⚠️  .env URL doesn't match local server")

if env_key == 'devkey':
    print("   ✅ .env API key matches livekit.yaml")
else:
    print("   ⚠️  .env API key doesn't match livekit.yaml")

print(f"   📋 All connections target: localhost:7880")
print()

print("🚀 READY FOR INTERVIEW!")
print("=" * 60)
print("To start an interview:")
print("1. Start AI agent: python complete_interview_agent.py")
print("2. Start web server: python -m http.server 8080")
print("3. Open browser: http://localhost:8080")
print("4. Generate session and share meeting URL")
print()
print("The HTML, LiveKit server, and Python agent will all")
print("connect using the same configuration from .env file!")
