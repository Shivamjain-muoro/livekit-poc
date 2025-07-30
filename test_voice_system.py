"""
Quick Voice Test
================
Simple test to verify TTS and STT capabilities are working.
"""

import asyncio
import logging

# Test TTS
def test_tts():
    """Test Text-to-Speech"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        
        test_message = "Hello! Your voice interview system is working perfectly!"
        print(f"🔊 Speaking: {test_message}")
        
        engine.say(test_message)
        engine.runAndWait()
        
        print("✅ Text-to-Speech test successful!")
        return True
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return False

# Test STT setup
def test_stt_setup():
    """Test Speech-to-Text setup"""
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        
        # List available microphones
        mics = sr.Microphone.list_microphone_names()
        print(f"🎤 Found {len(mics)} microphone(s)")
        
        if mics:
            print(f"Default microphone: {mics[0]}")
        
        print("✅ Speech-to-Text setup successful!")
        return True
    except Exception as e:
        print(f"❌ STT Error: {e}")
        return False

# Test Google Gemini
async def test_gemini():
    """Test Google Gemini integration"""
    try:
        import google.generativeai as genai
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            print("⚠️ GOOGLE_API_KEY not set in .env file")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test generation
        response = await asyncio.to_thread(
            model.generate_content, 
            "Say 'Hello from Gemini!' in a friendly way."
        )
        
        print(f"🤖 Gemini response: {response.text}")
        print("✅ Google Gemini test successful!")
        return True
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return False

async def main():
    """Run all voice tests"""
    print("🎙️ Voice Interview System Test")
    print("=" * 40)
    
    # Test components
    tts_ok = test_tts()
    print()
    
    stt_ok = test_stt_setup()
    print()
    
    gemini_ok = await test_gemini()
    print()
    
    # Summary
    print("📊 Test Results:")
    print(f"TTS (Text-to-Speech): {'✅' if tts_ok else '❌'}")
    print(f"STT (Speech-to-Text): {'✅' if stt_ok else '❌'}")
    print(f"Google Gemini: {'✅' if gemini_ok else '❌'}")
    
    if all([tts_ok, stt_ok, gemini_ok]):
        print("\n🎉 All voice systems working! Ready for interviews!")
    else:
        print("\n⚠️ Some components need attention.")
    
    print("\n📋 Next Steps:")
    print("1. Start backend: python realtime_voice_backend.py")
    print("2. Open demo: http://localhost:8003/voice-demo")
    print("3. Create voice interview and test!")

if __name__ == "__main__":
    asyncio.run(main())
