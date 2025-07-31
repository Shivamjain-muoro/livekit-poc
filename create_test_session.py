"""
Simple Test Client for Pure LiveKit Interview Agent
Creates a room token and provides connection instructions
"""

import os
import uuid
from dotenv import load_dotenv
from livekit.api import AccessToken, VideoGrants

load_dotenv()

# LiveKit configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")

def create_test_interview_session():
    """Create a test interview session with room token"""
    
    # Generate session details
    session_id = str(uuid.uuid4())[:8]
    room_name = f"interview_{session_id}"
    candidate_name = "Test Candidate"
    
    # Create access token for candidate
    token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    token.identity = f"candidate_{session_id}"
    token.with_grants(VideoGrants(
        room_join=True,
        room=room_name,
        can_publish=True,
        can_subscribe=True,
        can_publish_data=True
    ))
    
    access_token = token.to_jwt()
    
    print("🎙️ Pure LiveKit Interview Test Session Created!")
    print("=" * 60)
    print(f"📋 Session ID: {session_id}")
    print(f"🏠 Room Name: {room_name}")
    print(f"👤 Candidate: {candidate_name}")
    print(f"🔗 LiveKit URL: {LIVEKIT_URL}")
    print()
    print("🎯 Access Token:")
    print(access_token)
    print()
    print("📱 How to Test:")
    print("1. Start the agent: python pure_livekit_interview_agent.py")
    print("2. Use LiveKit web client or mobile app")
    print("3. Connect with the token above")
    print("4. The AI interviewer will start speaking automatically")
    print()
    print("🌐 Web Client URL:")
    print("https://meet.livekit.io/custom")
    print("(Use the LiveKit URL and token above)")
    print()
    
    return {
        "session_id": session_id,
        "room_name": room_name,
        "access_token": access_token,
        "livekit_url": LIVEKIT_URL
    }

if __name__ == "__main__":
    create_test_interview_session()
