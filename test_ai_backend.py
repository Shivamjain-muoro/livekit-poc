"""
Direct test of AI backend functionality
"""
import sys
import os

print("=" * 50)
print("TESTING AI BACKEND STEP BY STEP")
print("=" * 50)

# Change to project directory
os.chdir(r"C:\Users\ADMIN\projects\livekit-poc")
print(f"Current directory: {os.getcwd()}")

# Test environment loading
print("\n1. Testing environment loading...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    google_key = os.getenv('GOOGLE_API_KEY')
    livekit_url = os.getenv('LIVEKIT_URL')
    print(f"✅ Environment loaded - Google API: {'Set' if google_key else 'Missing'}")
    print(f"✅ LiveKit URL: {livekit_url}")
except Exception as e:
    print(f"❌ Environment error: {e}")
    sys.exit(1)

# Test Google AI import
print("\n2. Testing Google AI import...")
try:
    import google.generativeai as genai
    if google_key:
        genai.configure(api_key=google_key)
        print("✅ Google AI configured successfully")
        ai_available = True
    else:
        print("⚠️ Google AI key missing")
        ai_available = False
except Exception as e:
    print(f"❌ Google AI error: {e}")
    ai_available = False

# Test question generation
if ai_available:
    print("\n3. Testing AI question generation...")
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = """Generate 3 interview questions for a mid-level Python developer.
        Format: Return only the questions, one per line."""
        
        response = model.generate_content(prompt)
        if response.text:
            questions = [q.strip() for q in response.text.split('\n') if q.strip()]
            print(f"✅ Generated {len(questions)} questions:")
            for i, q in enumerate(questions[:3], 1):
                print(f"   {i}. {q}")
        else:
            print("❌ No response from AI")
    except Exception as e:
        print(f"❌ AI question generation error: {e}")

print("\n4. Testing FastAPI import...")
try:
    from fastapi import FastAPI
    print("✅ FastAPI imported successfully")
except Exception as e:
    print(f"❌ FastAPI error: {e}")

print("\n5. Testing LiveKit import...")
try:
    from livekit.api import AccessToken
    from livekit.api.access_token import VideoGrants
    print("✅ LiveKit imported successfully")
except Exception as e:
    print(f"❌ LiveKit error: {e}")

print("\n6. Testing models import...")
try:
    from models.interview_models import Candidate, SessionCreateRequest
    print("✅ Models imported successfully")
except Exception as e:
    print(f"❌ Models error: {e}")

print("\n7. Testing token generation...")
try:
    token = AccessToken("test_key", "test_secret") \
        .with_identity("test_user") \
        .with_name("Test User") \
        .with_grants(VideoGrants(
            room_join=True,
            room="test_room"
        )).to_jwt()
    print("✅ LiveKit token generated successfully")
except Exception as e:
    print(f"❌ Token generation error: {e}")

print("\n" + "=" * 50)
print("AI BACKEND TEST COMPLETE")
print("=" * 50)

if ai_available:
    print("🎉 All systems ready for AI-enhanced interviews!")
else:
    print("⚠️ AI disabled - will use fallback questions")
