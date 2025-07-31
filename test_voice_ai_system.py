"""
Quick Test Script for Voice AI Interview System
==============================================
Tests the core components without requiring full LiveKit setup.
"""

import asyncio
import json
import os
from datetime import datetime

# Test imports
try:
    import google.generativeai as genai
    print("✅ Google Generative AI imported successfully")
except ImportError:
    print("❌ Google Generative AI not available")

try:
    import speech_recognition as sr
    print("✅ Speech Recognition imported successfully")
except ImportError:
    print("❌ Speech Recognition not available")

try:
    from gtts import gTTS
    print("✅ Google Text-to-Speech imported successfully")
except ImportError:
    print("❌ Google Text-to-Speech not available")

try:
    import pygame
    print("✅ Pygame audio imported successfully")
except ImportError:
    print("❌ Pygame not available")

# Load environment
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def test_ai_question_generation():
    """Test AI question generation"""
    print("\n🧠 Testing AI Question Generation...")
    
    if not GOOGLE_API_KEY:
        print("❌ No Google API key - skipping AI test")
        return False
    
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        Generate 3 interview questions for a senior Software Engineer with Python, React skills.
        Return as JSON array with format:
        [{"question_text": "...", "question_type": "...", "skills_tested": [...]}]
        """
        
        response = model.generate_content(prompt)
        questions = json.loads(response.text.strip())
        
        print(f"✅ Generated {len(questions)} AI questions")
        for i, q in enumerate(questions):
            print(f"   {i+1}. {q['question_text'][:50]}...")
        
        return True
    
    except Exception as e:
        print(f"❌ AI question generation failed: {e}")
        return False

def test_ai_evaluation():
    """Test AI answer evaluation"""
    print("\n📊 Testing AI Answer Evaluation...")
    
    if not GOOGLE_API_KEY:
        print("❌ No Google API key - skipping AI test")
        return False
    
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        evaluation_prompt = """
        Evaluate this interview answer:
        Question: "Tell me about your experience with Python"
        Answer: "I've been using Python for 5 years, building web APIs with Django and Flask, data analysis with pandas, and machine learning with scikit-learn."
        
        Return JSON: {"score": <1-10>, "feedback": "...", "spoken_feedback": "..."}
        """
        
        response = model.generate_content(evaluation_prompt)
        evaluation = json.loads(response.text.strip())
        
        print(f"✅ Answer evaluation successful")
        print(f"   Score: {evaluation['score']}/10")
        print(f"   Feedback: {evaluation['feedback'][:50]}...")
        
        return True
    
    except Exception as e:
        print(f"❌ AI evaluation failed: {e}")
        return False

def test_speech_recognition():
    """Test speech recognition setup"""
    print("\n🎤 Testing Speech Recognition Setup...")
    
    try:
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 1.0
        
        print("✅ Speech recognizer configured successfully")
        print(f"   Energy threshold: {recognizer.energy_threshold}")
        print(f"   Pause threshold: {recognizer.pause_threshold}s")
        
        # Test microphone availability
        mic_list = sr.Microphone.list_microphone_names()
        print(f"✅ Found {len(mic_list)} microphones")
        
        return True
    
    except Exception as e:
        print(f"❌ Speech recognition setup failed: {e}")
        return False

def test_tts_system():
    """Test text-to-speech system"""
    print("\n🗣️ Testing Text-to-Speech System...")
    
    try:
        # Test gTTS
        test_text = "Hello! This is a test of the AI interview system."
        tts = gTTS(text=test_text, lang='en', slow=False)
        
        print("✅ gTTS object created successfully")
        
        # Test pygame mixer
        pygame.mixer.init()
        print("✅ pygame audio mixer initialized")
        
        return True
    
    except Exception as e:
        print(f"❌ TTS system test failed: {e}")
        return False

async def test_api_endpoints():
    """Test API endpoints are working"""
    print("\n🌐 Testing API Endpoints...")
    
    try:
        import httpx
        
        # Test health endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/health")
            if response.status_code == 200:
                health_data = response.json()
                print("✅ Health endpoint working")
                print(f"   AI Status: {'Enabled' if health_data.get('ai_enabled') else 'Disabled'}")
                print(f"   LiveKit URL: {health_data.get('livekit_url')}")
                return True
            else:
                print(f"❌ Health endpoint returned {response.status_code}")
                return False
    
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        print("   (This is normal if the server isn't running yet)")
        return False

def test_livekit_configuration():
    """Test LiveKit configuration"""
    print("\n🎙️ Testing LiveKit Configuration...")
    
    try:
        from livekit.api import AccessToken
        from livekit.api.access_token import VideoGrants
        
        LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
        LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")
        
        # Test token generation
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
        jwt_token = token.to_jwt()
        
        print("✅ LiveKit token generation successful")
        print(f"   Token length: {len(jwt_token)} characters")
        
        return True
    
    except Exception as e:
        print(f"❌ LiveKit configuration test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Voice AI Interview System - Component Tests")
    print("=" * 50)
    
    tests = [
        ("AI Question Generation", test_ai_question_generation),
        ("AI Answer Evaluation", test_ai_evaluation),
        ("Speech Recognition", test_speech_recognition),
        ("Text-to-Speech", test_tts_system),
        ("LiveKit Configuration", test_livekit_configuration),
        ("API Endpoints", test_api_endpoints)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All systems ready for voice AI interviews!")
        print("\n🚀 Next steps:")
        print("1. Start LiveKit server: start_livekit_npm.bat")
        print("2. Access the interface: http://localhost:8001/voice-ai")
    else:
        print(f"\n⚠️ {total - passed} tests failed - check configuration")
        print("\n🔧 Common fixes:")
        if not results.get("AI Question Generation", False):
            print("- Set GOOGLE_API_KEY in .env file")
        if not results.get("LiveKit Configuration", False):
            print("- Install livekit-api: pip install livekit-api")
        if not results.get("Speech Recognition", False):
            print("- Install SpeechRecognition: pip install SpeechRecognition")

if __name__ == "__main__":
    asyncio.run(main())
