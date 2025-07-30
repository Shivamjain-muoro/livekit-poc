"""
Minimal Enhanced AI Backend Test - Testing imports step by step
"""
import os
import sys

print("Starting import tests...")

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment loaded")
except Exception as e:
    print(f"❌ Environment error: {e}")

try:
    import google.generativeai as genai
    print("✅ Google AI imported")
except Exception as e:
    print(f"❌ Google AI error: {e}")

try:
    from fastapi import FastAPI
    print("✅ FastAPI imported")
except Exception as e:
    print(f"❌ FastAPI error: {e}")

try:
    from livekit.api import AccessToken
    print("✅ LiveKit imported")
except Exception as e:
    print(f"❌ LiveKit error: {e}")

# Test environment variables
google_api_key = os.getenv('GOOGLE_API_KEY')
print(f"Google API Key: {'✅ Found' if google_api_key else '❌ Missing'}")

if google_api_key:
    try:
        genai.configure(api_key=google_api_key)
        print("✅ Google AI configured")
    except Exception as e:
        print(f"❌ Google AI config error: {e}")

print("\n🎉 All basic imports working! Now testing enhanced backend...")

# Test enhanced backend import
try:
    import enhanced_ai_backend
    print("✅ Enhanced backend imported successfully")
except Exception as e:
    print(f"❌ Enhanced backend import error: {e}")
    print(f"Error details: {type(e).__name__}: {str(e)}")
