#!/usr/bin/env python3
"""
Test script to verify all imports for enhanced AI backend
"""

import sys
import os
print("✅ Python and OS imports successful")

try:
    import fastapi
    from fastapi import FastAPI, HTTPException
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse
    from fastapi.middleware.cors import CORSMiddleware
    print("✅ FastAPI imports successful")
except ImportError as e:
    print(f"❌ FastAPI import error: {e}")
    sys.exit(1)

try:
    import google.generativeai as genai
    print("✅ Google Generative AI import successful")
except ImportError as e:
    print(f"❌ Google Generative AI import error: {e}")
    sys.exit(1)

try:
    from livekit.api import AccessToken
    print("✅ LiveKit AccessToken import successful")
except ImportError as e:
    print(f"❌ LiveKit import error: {e}")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    print("✅ dotenv import successful")
except ImportError as e:
    print(f"❌ dotenv import error: {e}")
    sys.exit(1)

try:
    import sqlite3
    import json
    import datetime
    import uuid
    import logging
    print("✅ Standard library imports successful")
except ImportError as e:
    print(f"❌ Standard library import error: {e}")
    sys.exit(1)

print("\n🎉 All imports successful! Enhanced backend should work.")

# Test environment loading
load_dotenv()
google_api_key = os.getenv('GOOGLE_API_KEY')
livekit_url = os.getenv('LIVEKIT_URL')
livekit_api_key = os.getenv('LIVEKIT_API_KEY')

print(f"\n📋 Environment Variables:")
print(f"Google API Key: {'✅ Set' if google_api_key else '❌ Missing'}")
print(f"LiveKit URL: {livekit_url if livekit_url else '❌ Missing'}")
print(f"LiveKit API Key: {'✅ Set' if livekit_api_key else '❌ Missing'}")

# Test Google AI configuration
if google_api_key:
    try:
        genai.configure(api_key=google_api_key)
        print("✅ Google AI configured successfully")
    except Exception as e:
        print(f"❌ Google AI configuration error: {e}")

print("\n🚀 Ready to test enhanced backend!")
