"""
Auto-Interview Manager
Creates rooms and manages interview sessions automatically
"""

import os
import uuid
from dotenv import load_dotenv
from livekit.api import AccessToken, VideoGrants

load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")

class InterviewManager:
    def __init__(self):
        pass
    
    def create_interview_session(self, candidate_info: dict):
        """Create a new interview session and return connection details"""
        
        session_id = str(uuid.uuid4())[:8]
        room_name = f"interview_{session_id}"
        
        print(f"✅ Creating interview session: {room_name}")
        
        # Generate candidate token
        candidate_token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        candidate_token.identity = f"candidate_{session_id}"
        candidate_token.with_grants(VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True
        ))
        
        # Store candidate info
        candidate_metadata = {
            "name": candidate_info.get("name", "Test Candidate"),
            "position": candidate_info.get("position", "Software Developer"),
            "experience_level": candidate_info.get("experience_level", "mid"),
            "skills": candidate_info.get("skills", "Python, JavaScript")
        }
        
        return {
            "session_id": session_id,
            "room_name": room_name,
            "candidate_token": candidate_token.to_jwt(),
            "livekit_url": LIVEKIT_URL,
            "candidate_info": candidate_metadata
        }
    
    def print_connection_info(self, session_info):
        """Print connection information for candidate"""
        print("🎙️ Interview Session Created!")
        print("=" * 50)
        print(f"📋 Session ID: {session_info['session_id']}")
        print(f"🏠 Room Name: {session_info['room_name']}")
        print(f"👤 Candidate: {session_info['candidate_info']['name']}")
        print(f"💼 Position: {session_info['candidate_info']['position']}")
        print()
        print("🔗 Connection Details:")
        print(f"   LiveKit URL: {session_info['livekit_url']}")
        print(f"   Access Token: {session_info['candidate_token']}")
        print()
        print("🌐 Quick Join Links:")
        print("   Web Client: https://meet.livekit.io/custom")
        print("   (Use the URL and token above)")
        print()
        print("📱 Mobile Apps:")
        print("   - iOS: LiveKit Example App")
        print("   - Android: LiveKit Example App")
        print()

def main():
    """Create a test interview session"""
    manager = InterviewManager()
    
    # Example candidate information
    candidate_info = {
        "name": "John Doe",
        "position": "Senior Software Engineer",
        "experience_level": "senior",
        "skills": "Python, React, Node.js, AWS, Docker"
    }
    
    print("🚀 Creating Interview Session...")
    print()
    
    session_info = manager.create_interview_session(candidate_info)
    manager.print_connection_info(session_info)
    
    print("⚡ Next Steps:")
    print("1. Make sure the agent is running: python pure_livekit_interview_agent.py dev")
    print("2. Candidate joins using the connection details above")
    print("3. Interview starts automatically when candidate joins")
    print()

if __name__ == "__main__":
    main()
