"""
Test Google Realtime API Authentication
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def test_google_realtime():
    """Test Google Realtime API authentication"""
    
    print("🔍 Testing Google Realtime API")
    print("=" * 40)
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Configure the API
    try:
        genai.configure(api_key=api_key)
        print("✅ Google API configured")
    except Exception as e:
        print(f"❌ Failed to configure Google API: {e}")
        return False
    
    # Test listing models
    try:
        models = list(genai.list_models())
        print(f"✅ Found {len(models)} available models")
        
        # Check for realtime models
        realtime_models = [m for m in models if 'realtime' in m.name.lower()]
        if realtime_models:
            print(f"✅ Found realtime models: {[m.name for m in realtime_models]}")
        else:
            print("⚠️  No realtime models found in listing")
            
    except Exception as e:
        print(f"❌ Failed to list models: {e}")
        return False
    
    print("\n✅ Google Realtime API test passed!")
    return True

if __name__ == "__main__":
    test_google_realtime()
