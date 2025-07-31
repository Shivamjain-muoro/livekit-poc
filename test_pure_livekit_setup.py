"""
Quick Test Script for Pure LiveKit Interview Agent
Tests dependencies and configuration before starting the full agent
"""

import sys
import os

def test_dependencies():
    """Test if all required packages are installed"""
    print("🔍 Testing Pure LiveKit Interview Agent Dependencies")
    print("=" * 60)
    
    missing_packages = []
    
    # Test core packages
    try:
        import livekit.agents
        print("✅ livekit.agents - OK")
    except ImportError:
        print("❌ livekit.agents - MISSING")
        missing_packages.append("livekit-agents")
    
    try:
        import livekit.api
        print("✅ livekit.api - OK")
    except ImportError:
        print("❌ livekit.api - MISSING")
        missing_packages.append("livekit-api")
    
    try:
        import livekit.rtc
        print("✅ livekit.rtc - OK")
    except ImportError:
        print("❌ livekit.rtc - MISSING")
        missing_packages.append("livekit-rtc")
    
    try:
        from livekit.plugins import google
        print("✅ livekit.plugins.google - OK")
    except ImportError:
        print("❌ livekit.plugins.google - MISSING")
        missing_packages.append("livekit-plugins-google")
    
    try:
        import google.generativeai
        print("✅ google.generativeai - OK")
    except ImportError:
        print("❌ google.generativeai - MISSING")
        missing_packages.append("google-generativeai")
    
    try:
        import dotenv
        print("✅ python-dotenv - OK")
    except ImportError:
        print("❌ python-dotenv - MISSING")
        missing_packages.append("python-dotenv")
    
    print()
    
    if missing_packages:
        print("❌ Missing packages detected!")
        print("   Run this command to install them:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    else:
        print("✅ All dependencies are installed!")
        return True

def test_environment():
    """Test environment configuration"""
    print("🔧 Testing Environment Configuration")
    print("=" * 40)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check required environment variables
    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_key = os.getenv("LIVEKIT_API_KEY")
    livekit_secret = os.getenv("LIVEKIT_API_SECRET")
    google_key = os.getenv("GOOGLE_API_KEY")
    
    if livekit_url:
        print(f"✅ LIVEKIT_URL: {livekit_url}")
    else:
        print("❌ LIVEKIT_URL not set")
    
    if livekit_key:
        print(f"✅ LIVEKIT_API_KEY: {livekit_key}")
    else:
        print("❌ LIVEKIT_API_KEY not set")
    
    if livekit_secret:
        print(f"✅ LIVEKIT_API_SECRET: {livekit_secret[:8]}...")
    else:
        print("❌ LIVEKIT_API_SECRET not set")
    
    if google_key:
        print(f"✅ GOOGLE_API_KEY: {google_key[:8]}...")
    else:
        print("❌ GOOGLE_API_KEY not set")
    
    print()
    return all([livekit_url, livekit_key, livekit_secret, google_key])

def test_agent_files():
    """Test if all agent files exist"""
    print("📁 Testing Agent Files")
    print("=" * 25)
    
    required_files = [
        "pure_livekit_interview_agent.py",
        "interview_tools.py", 
        "interview_prompts.py",
        ".env"
    ]
    
    all_files_exist = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_files_exist = False
    
    print()
    return all_files_exist

if __name__ == "__main__":
    print("🎙️ Pure LiveKit Interview Agent - Dependency Test")
    print("=" * 70)
    print()
    
    # Run all tests
    deps_ok = test_dependencies()
    env_ok = test_environment()
    files_ok = test_agent_files()
    
    print("🎯 Test Summary")
    print("=" * 20)
    
    if deps_ok and env_ok and files_ok:
        print("✅ ALL TESTS PASSED!")
        print()
        print("🚀 Ready to start Pure LiveKit Interview Agent!")
        print()
        print("Next steps:")
        print("1. Start LiveKit server: npx @livekit/livekit-server --dev --keys devkey:secret")
        print("2. Start interview agent: python pure_livekit_interview_agent.py")
        print()
    else:
        print("❌ Some tests failed. Please fix the issues above before proceeding.")
        print()
        
        if not deps_ok:
            print("📦 Install missing dependencies first")
        if not env_ok:
            print("🔧 Configure .env file with correct API keys")
        if not files_ok:
            print("📁 Ensure all required files are present")
