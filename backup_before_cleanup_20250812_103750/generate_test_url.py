"""
Generate Test URL for Interview
Run this to get a URL that a candidate can use to join the interview
"""

import os
from dotenv import load_dotenv
from livekit import api
import secrets

# Load environment variables
load_dotenv()

def generate_interview_url():
    """Generate a test URL for joining the interview"""
    
    livekit_url = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
    livekit_key = os.getenv("LIVEKIT_API_KEY", "devkey")
    livekit_secret = os.getenv("LIVEKIT_API_SECRET", "secret")
    
    # Generate unique room name
    room_name = f"interview_{secrets.token_hex(4)}"
    
    # Create room token for candidate
    token = api.AccessToken(livekit_key, livekit_secret) \
        .with_identity("candidate") \
        .with_name("Interview Candidate") \
        .with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
        )) \
        .to_jwt()
    
    print("🎯 Interview Room Generated!")
    print("=" * 50)
    print(f"Room Name: {room_name}")
    print(f"LiveKit URL: {livekit_url}")
    print(f"Token: {token[:50]}...")
    print()
    print("🌐 CANDIDATE TEST URL:")
    print(f"https://meet.livekit.io/custom?liveKitUrl={livekit_url}&token={token}")
    print()
    print("📱 MOBILE TEST (QR CODE):")
    print("Use a QR code generator with the URL above")
    print()
    print("🧪 BROWSER TEST:")
    print("1. Open the URL above in your browser")
    print("2. Allow microphone permissions")
    print("3. Join the room")
    print("4. The AI agent should greet you and start the interview!")
    print()
    print("📊 MONITOR INTERVIEW:")
    print("- Check agent logs in the terminal running complete_interview_agent.py")
    print("- View database: python -c \"import sqlite3; conn=sqlite3.connect('database/interview_sessions.db'); print(conn.execute('SELECT * FROM candidate_profiles').fetchall()); conn.close()\"")
    
    return {
        "room_name": room_name,
        "token": token,
        "url": f"https://meet.livekit.io/custom?liveKitUrl={livekit_url}&token={token}"
    }

if __name__ == "__main__":
    generate_interview_url()
