"""
Quick Backend Test
=================
Test if the enhanced backend is running and accessible.
"""

import requests
import asyncio
import aiohttp

def test_enhanced_backend():
    """Test the enhanced backend on port 8002"""
    base_url = "http://localhost:8002"
    
    print("🧪 Testing Enhanced Backend (Port 8002)")
    print("=" * 45)
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Enhanced backend is running!")
            print(f"Health status: {response.json()}")
            return True
        else:
            print(f"⚠️ Backend responding with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Enhanced backend not running on port 8002")
        print("💡 Start with: python enhanced_backend.py")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_voice_backend():
    """Test the voice backend on port 8003"""
    base_url = "http://localhost:8003"
    
    print("\n🧪 Testing Voice Backend (Port 8003)")
    print("=" * 42)
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Voice backend is running!")
            print(f"Health status: {response.json()}")
            return True
        else:
            print(f"⚠️ Backend responding with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Voice backend not running on port 8003")
        print("💡 Start with: python realtime_voice_backend.py")
        return False
    except Exception as e:
        print(f"❌ Error testing voice backend: {e}")
        return False

def main():
    """Run backend tests"""
    print("🚀 Backend Connection Test")
    print("=" * 30)
    
    enhanced_ok = test_enhanced_backend()
    voice_ok = test_voice_backend()
    
    print("\n📊 Results:")
    print(f"Enhanced Backend (8002): {'✅' if enhanced_ok else '❌'}")
    print(f"Voice Backend (8003): {'✅' if voice_ok else '❌'}")
    
    if enhanced_ok:
        print("\n🎯 UI Testing URLs:")
        print("📝 Simple Interface: http://localhost:8002/simple")
        print("🎥 Live Interface: http://localhost:8002/live-fixed")
        print("📚 API Docs: http://localhost:8002/docs")
    
    if voice_ok:
        print("🎙️ Voice Demo: http://localhost:8003/voice-demo")
        print("📚 Voice API: http://localhost:8003/docs")
    
    if not enhanced_ok and not voice_ok:
        print("\n💡 Quick Start:")
        print("1. Open PowerShell in the project directory")
        print("2. Run: python enhanced_backend.py")
        print("3. Open: http://localhost:8002/simple")

if __name__ == "__main__":
    main()
