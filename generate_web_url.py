"""
Generate Complete LiveKit Web Client URL
Creates the proper URL with parameters for direct access
"""

import os
import uuid
from urllib.parse import quote
from dotenv import load_dotenv
from livekit.api import AccessToken, VideoGrants

load_dotenv()

def generate_web_client_url():
    """Generate complete URL for LiveKit web client"""
    
    LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
    LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
    LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")
    
    # Create session details
    session_id = str(uuid.uuid4())[:8]
    room_name = f"interview_{session_id}"
    
    # Generate token
    token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    token.identity = f"candidate_{session_id}"
    token.with_grants(VideoGrants(
        room_join=True,
        room=room_name,
        can_publish=True,
        can_subscribe=True,
        can_publish_data=True
    ))
    
    jwt_token = token.to_jwt()
    
    # Create complete URL with parameters
    base_url = "https://meet.livekit.io/custom"
    encoded_url = quote(LIVEKIT_URL, safe=':/')
    encoded_token = quote(jwt_token, safe='')
    
    complete_url = f"{base_url}?liveKitUrl={encoded_url}&token={encoded_token}"
    
    print("🎙️ LiveKit Web Client - Direct Access")
    print("=" * 50)
    print(f"📋 Session ID: {session_id}")
    print(f"🏠 Room Name: {room_name}")
    print(f"👤 Identity: candidate_{session_id}")
    print()
    print("🔗 Complete Web Client URL:")
    print("=" * 30)
    print(complete_url)
    print()
    print("📋 Manual Parameters (if needed):")
    print(f"   LiveKit URL: {LIVEKIT_URL}")
    print(f"   Token: {jwt_token}")
    print()
    print("🚀 Instructions:")
    print("1. Make sure your agent is running: python pure_livekit_interview_agent.py dev")
    print("2. Copy the complete URL above")
    print("3. Paste it in your browser")
    print("4. Grant microphone permissions when prompted")
    print("5. The AI interviewer should start speaking!")
    print()
    
    return {
        "session_id": session_id,
        "room_name": room_name,
        "livekit_url": LIVEKIT_URL,
        "token": jwt_token,
        "web_client_url": complete_url
    }

if __name__ == "__main__":
    generate_web_client_url()
