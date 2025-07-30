"""
Quick test to check if the AI backend server is running
"""
import requests
import time

def test_server():
    print("🔍 Testing AI Backend Server...")
    
    # Wait a moment for server to start
    time.sleep(3)
    
    try:
        # Test health endpoint
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is running!")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   AI Status: {data.get('ai_status', 'unknown')}")
            print(f"   LiveKit: {data.get('livekit_configured', False)}")
            print(f"   Timestamp: {data.get('timestamp', 'unknown')}")
            return True
        else:
            print(f"❌ Server responded with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server at http://localhost:8000")
        print("   Make sure the server is running!")
        return False
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

if __name__ == "__main__":
    if test_server():
        print("\n🎉 Server is ready for testing!")
        print("\n📝 Available endpoints:")
        print("   🏠 Home: http://localhost:8000")
        print("   🔗 Enhanced UI: http://localhost:8000/enhanced")
        print("   📱 Local LiveKit: http://localhost:8000/live-local")
        print("   💻 Simple UI: http://localhost:8000/simple")
        print("   ❤️ Health Check: http://localhost:8000/health")
    else:
        print("\n⚠️ Server not responding. Please check:")
        print("   1. Is the server running?")
        print("   2. Is port 8000 available?")
        print("   3. Check the server console for errors")
