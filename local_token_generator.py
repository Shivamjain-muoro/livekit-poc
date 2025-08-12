"""
Local LiveKit Token Generator
Generates JWT tokens for local LiveKit server access
"""

import jwt
import time
import uuid
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/.env')

class LocalTokenGenerator:
    def __init__(self):
        self.api_key = os.getenv('LIVEKIT_API_KEY', 'devkey')
        self.api_secret = os.getenv('LIVEKIT_API_SECRET', 'secret')
        self.livekit_url = os.getenv('LIVEKIT_URL', 'ws://localhost:7880')
        
    def generate_token(self, room_name, participant_name="Interview Candidate", participant_identity=None):
        """Generate JWT token for local LiveKit server"""
        
        if not participant_identity:
            participant_identity = f"candidate_{uuid.uuid4().hex[:8]}"
        
        now = datetime.utcnow()
        exp = now + timedelta(hours=6)  # 6 hour expiry
        
        payload = {
            "iss": self.api_key,
            "sub": participant_identity,
            "name": participant_name,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
            "video": {
                "roomJoin": True,
                "room": room_name,
                "canPublish": True,
                "canSubscribe": True,
                "canPublishData": True,
                "canUpdateOwnMetadata": True
            }
        }
        
        token = jwt.encode(payload, self.api_secret, algorithm="HS256")
        return token
    
    def generate_interview_session(self, candidate_name="Interview Candidate", position="Applied Position"):
        """Generate complete interview session with room and token"""
        
        # Generate unique room name
        room_name = f"interview_{uuid.uuid4().hex[:8]}"
        
        # Generate token
        token = self.generate_token(room_name, candidate_name)
        
        # Create session info
        session_info = {
            "session_id": room_name,
            "room_name": room_name,
            "candidate_name": candidate_name,
            "position": position,
            "token": token,
            "livekit_url": self.livekit_url,
            "meeting_url": f"http://localhost:8080/interview.html?room={room_name}&token={token}",
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=6)).isoformat()
        }
        
        return session_info
    
    def get_meeting_url_with_token(self, room_name=None, candidate_name="Interview Candidate"):
        """Generate meeting URL with embedded token for easy sharing"""
        
        if not room_name:
            room_name = f"interview_{uuid.uuid4().hex[:8]}"
            
        token = self.generate_token(room_name, candidate_name)
        
        # Create URL parameters
        params = {
            "room": room_name,
            "token": token,
            "name": candidate_name,
            "url": self.livekit_url
        }
        
        # Build complete URL
        base_url = "http://localhost:8080/interview.html"
        url_params = "&".join([f"{k}={v}" for k, v in params.items()])
        complete_url = f"{base_url}?{url_params}"
        
        return {
            "room_name": room_name,
            "meeting_url": complete_url,
            "token": token,
            "expires_in_hours": 6
        }

def main():
    """CLI interface for generating tokens and URLs"""
    print("🏠 LOCAL LIVEKIT TOKEN GENERATOR")
    print("=" * 50)
    
    generator = LocalTokenGenerator()
    
    print(f"🔗 LiveKit URL: {generator.livekit_url}")
    print(f"🔑 API Key: {generator.api_key}")
    print()
    
    # Generate new interview session
    session = generator.generate_interview_session()
    
    print("✅ NEW INTERVIEW SESSION GENERATED:")
    print(f"📋 Session ID: {session['session_id']}")
    print(f"👤 Candidate: {session['candidate_name']}")
    print(f"💼 Position: {session['position']}")
    print(f"🔗 Meeting URL: {session['meeting_url']}")
    print(f"⏰ Expires: {session['expires_at']}")
    print()
    print("🎯 READY TO START:")
    print("1. Start LiveKit server: docker-compose up livekit")
    print("2. Start AI agent: python complete_interview_agent.py")
    print("3. Start web server: python -m http.server 8080")
    print("4. Open meeting URL in browser")
    print()
    print("🎫 Token (first 50 chars):", session['token'][:50] + "...")
    
    return session

if __name__ == "__main__":
    main()
