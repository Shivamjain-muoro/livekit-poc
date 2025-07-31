"""
Test Pure LiveKit Implementation
"""

try:
    from livekit import rtc, api
    from livekit.api import AccessToken
    from livekit.api.access_token import VideoGrants
    print("✅ LiveKit imports successful")
    
    # Test token creation
    token = AccessToken("devkey", "secret", identity="test")
    token.with_grants(VideoGrants(room_join=True, room="test"))
    jwt_token = token.to_jwt()
    print("✅ Access token creation successful")
    
    print("🎙️ Pure LiveKit system ready!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
