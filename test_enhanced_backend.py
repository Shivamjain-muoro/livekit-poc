"""
Test the enhanced AI backend components
"""
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Test imports
try:
    import google.generativeai as genai
    print("✅ Google Generative AI imported successfully")
except ImportError as e:
    print(f"❌ Google AI import failed: {e}")

try:
    from livekit.api import AccessToken
    from livekit.api.access_token import VideoGrants
    print("✅ LiveKit API imported successfully")
except ImportError as e:
    print(f"❌ LiveKit import failed: {e}")

try:
    from models.interview_models import Candidate
    print("✅ Interview models imported successfully")
except ImportError as e:
    print(f"❌ Models import failed: {e}")

# Test Google AI configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        print("✅ Google Gemini AI configured successfully")
        
        # Test a simple generation
        response = model.generate_content("Say hello in a friendly way")
        print(f"✅ AI Response: {response.text[:100]}...")
        
    except Exception as e:
        print(f"❌ Google AI configuration failed: {e}")
else:
    print("⚠️ No Google API key found in .env")

# Test LiveKit token generation
try:
    from datetime import timedelta
    
    LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
    LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")
    
    token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    token.with_identity("test-participant")
    token.with_name("Test User")
    
    grants = VideoGrants(
        room_join=True,
        room="test-room",
        can_publish=True,
        can_subscribe=True
    )
    
    token.with_grants(grants)
    token.with_ttl(timedelta(hours=1))
    
    jwt_token = token.to_jwt()
    print(f"✅ LiveKit token generated: {jwt_token[:50]}...")
    
except Exception as e:
    print(f"❌ LiveKit token generation failed: {e}")

print("\n🚀 All components tested!")
print("Ready to start enhanced AI backend")
