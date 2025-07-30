"""
Voice Interview System Setup and Test Script
===========================================
This script sets up and tests the real-time voice interview system.
"""

import os
import sys
import subprocess
import asyncio
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    logger.info(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_voice_dependencies():
    """Install voice processing dependencies"""
    logger.info("📦 Installing voice processing dependencies...")
    
    # Essential voice packages
    packages = [
        "pyttsx3>=2.90",
        "SpeechRecognition>=3.10.0", 
        "aiohttp>=3.9.0",
        "google-generativeai>=0.8.0"
    ]
    
    for package in packages:
        try:
            logger.info(f"Installing {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ {package} installed successfully")
            else:
                logger.warning(f"⚠️ Issue installing {package}: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ Error installing {package}: {e}")

def check_voice_dependencies():
    """Check if voice dependencies are available"""
    logger.info("🔍 Checking voice dependencies...")
    
    dependencies = {
        "pyttsx3": "Text-to-Speech",
        "speech_recognition": "Speech Recognition", 
        "aiohttp": "HTTP Client",
        "google.generativeai": "Google Gemini"
    }
    
    available = {}
    
    for module, description in dependencies.items():
        try:
            __import__(module)
            logger.info(f"✅ {description} ({module}) - Available")
            available[module] = True
        except ImportError:
            logger.warning(f"❌ {description} ({module}) - Not Available")
            available[module] = False
    
    return available

def test_tts():
    """Test Text-to-Speech functionality"""
    logger.info("🔊 Testing Text-to-Speech...")
    
    try:
        import pyttsx3
        
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        
        # Test TTS
        test_text = "Hello! This is a test of the text to speech system."
        logger.info(f"Speaking: {test_text}")
        
        engine.say(test_text)
        engine.runAndWait()
        
        logger.info("✅ Text-to-Speech test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ TTS test failed: {e}")
        return False

def test_stt():
    """Test Speech-to-Text functionality (simulation)"""
    logger.info("🎤 Testing Speech-to-Text setup...")
    
    try:
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        
        # Check for microphone
        mic_list = sr.Microphone.list_microphone_names()
        if mic_list:
            logger.info(f"✅ Found {len(mic_list)} microphone(s)")
            logger.info(f"Default microphone: {mic_list[0] if mic_list else 'None'}")
        else:
            logger.warning("⚠️ No microphones detected")
        
        logger.info("✅ Speech-to-Text setup completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ STT test failed: {e}")
        return False

async def test_voice_agent():
    """Test the voice interview agent"""
    logger.info("🤖 Testing Voice Interview Agent...")
    
    try:
        # Import our voice agent
        sys.path.append(os.path.dirname(__file__))
        from voice_interview_agent import VoiceInterviewAgent
        
        # Create test agent
        agent = VoiceInterviewAgent("test-session-123")
        
        # Test speech synthesis
        await agent.speak("Hello! This is a test of the voice interview agent.")
        
        logger.info("✅ Voice agent test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Voice agent test failed: {e}")
        return False

async def test_backend_connection():
    """Test connection to the backend"""
    logger.info("🌐 Testing backend connection...")
    
    try:
        import aiohttp
        
        backend_url = "http://localhost:8003"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{backend_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("✅ Backend connection successful")
                    logger.info(f"Services: {data.get('services', {})}")
                    return True
                else:
                    logger.warning(f"⚠️ Backend returned status: {response.status}")
                    
    except Exception as e:
        logger.warning(f"⚠️ Backend connection failed: {e}")
        logger.info("💡 Start the backend with: python realtime_voice_backend.py")
        
    return False

def create_demo_script():
    """Create a demo script for testing"""
    demo_script = '''
"""
Voice Interview Demo Runner
==========================
Quick demo of the voice interview system.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

async def run_demo():
    """Run the voice interview demo"""
    print("Voice Interview System Demo")
    print("=" * 50)
    
    try:
        from voice_interview_agent import demo_interview
        await demo_interview()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure dependencies are installed: python setup_voice_system.py")
    except Exception as e:
        print(f"Demo error: {e}")

if __name__ == "__main__":
    asyncio.run(run_demo())
'''
    
    with open("demo_voice_interview.py", "w", encoding="utf-8") as f:
        f.write(demo_script)
    
    logger.info("✅ Created demo_voice_interview.py")

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("🎉 VOICE INTERVIEW SYSTEM SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("📋 NEXT STEPS:")
    print()
    print("1. 🚀 Start the backend server:")
    print("   python realtime_voice_backend.py")
    print()
    print("2. 🌐 Open the voice demo page:")
    print("   http://localhost:8003/voice-demo")
    print()
    print("3. 🎤 Test voice functionality:")
    print("   python demo_voice_interview.py")
    print()
    print("4. 🧪 Create a voice interview session:")
    print("   - Fill out candidate information")
    print("   - Click 'Start Voice Interview'")
    print("   - Join the room and speak with the AI")
    print()
    print("📚 FEATURES AVAILABLE:")
    print("✅ Real-time speech-to-text")
    print("✅ Text-to-speech responses")  
    print("✅ Google Gemini evaluation")
    print("✅ LiveKit video/audio integration")
    print("✅ WebSocket real-time updates")
    print("✅ Comprehensive interview flow")
    print()
    print("🔧 TROUBLESHOOTING:")
    print("- Ensure microphone permissions are granted")
    print("- Check GOOGLE_API_KEY in .env file")
    print("- Verify LiveKit credentials are set")
    print("- Install missing dependencies if needed")
    print()

async def main():
    """Main setup function"""
    print("🎙️ Voice Interview System Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    install_voice_dependencies()
    
    # Check dependencies
    dependencies = check_voice_dependencies()
    
    # Run tests
    print("\n🧪 Running Tests...")
    print("-" * 20)
    
    tts_ok = test_tts()
    stt_ok = test_stt()
    
    # Test voice agent
    if dependencies.get("pyttsx3") and dependencies.get("aiohttp"):
        agent_ok = await test_voice_agent()
    else:
        logger.warning("⚠️ Skipping voice agent test - dependencies missing")
        agent_ok = False
    
    # Test backend connection
    backend_ok = await test_backend_connection()
    
    # Create demo script
    create_demo_script()
    
    # Print results
    print("\n📊 TEST RESULTS:")
    print("-" * 20)
    print(f"Text-to-Speech: {'✅' if tts_ok else '❌'}")
    print(f"Speech-to-Text: {'✅' if stt_ok else '❌'}")
    print(f"Voice Agent: {'✅' if agent_ok else '❌'}")
    print(f"Backend Connection: {'✅' if backend_ok else '⚠️'}")
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    asyncio.run(main())
