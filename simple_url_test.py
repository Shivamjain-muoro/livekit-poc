"""
Simple URL Generator (No Emojis)
Generates interview URLs without unicode issues
"""

import os
import uuid
from livekit import AccessToken, VideoGrants

def simple_url_test():
    """Generate URL without unicode issues"""
    print("TESTING URL GENERATION...")
    
    try:
        # Load environment
        from dotenv import load_dotenv
        load_dotenv()
        
        # Get credentials
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET") 
        livekit_url = os.getenv("LIVEKIT_URL")
        
        if not all([api_key, api_secret, livekit_url]):
            print("ERROR: Missing LiveKit credentials")
            return False
        
        # Generate room
        room_name = f"interview_{uuid.uuid4().hex[:8]}"
        
        # Create token
        token = AccessToken(api_key, api_secret)
        token.with_identity("interviewer")
        token.with_name("Interviewer")
        token.with_grants(VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True
        ))
        
        # Generate URL
        jwt_token = token.to_jwt()
        interview_url = f"https://meet.livekit.io/custom?liveKitUrl={livekit_url}&token={jwt_token}#room_name={room_name}"
        
        print("SUCCESS: URL Generated!")
        print(f"Room: {room_name}")
        print(f"URL: {interview_url[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    simple_url_test()
