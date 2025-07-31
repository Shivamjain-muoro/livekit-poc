"""
Test Google Voice Plugin
Verify that the Google real-time voice model is properly configured
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_google_voice():
    """Test Google voice plugin configuration"""
    
    print("🔍 Testing Google Voice Plugin Configuration")
    print("=" * 50)
    
    # Check Google API key
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        print(f"✅ GOOGLE_API_KEY: {google_key[:8]}...")
    else:
        print("❌ GOOGLE_API_KEY not found")
        return False
    
    # Test imports
    try:
        from livekit.plugins import google
        print("✅ livekit.plugins.google imported successfully")
    except ImportError as e:
        print(f"❌ Google plugin import failed: {e}")
        return False
    
    try:
        # Test creating the voice model
        model = google.beta.realtime.RealtimeModel(
            voice="Aoede",
            temperature=0.7,
        )
        print("✅ Google RealtimeModel created successfully")
        print(f"   Voice: Aoede")
        print(f"   Temperature: 0.7")
    except Exception as e:
        print(f"❌ Failed to create RealtimeModel: {e}")
        return False
    
    print()
    print("✅ Google Voice Plugin is properly configured!")
    return True

if __name__ == "__main__":
    test_google_voice()
