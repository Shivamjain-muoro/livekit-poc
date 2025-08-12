"""
Complete Interview Flow Test Script
This script will help you test the entire interview flow quickly
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_complete_flow():
    """Test the complete interview flow"""
    
    print("🧪 TESTING: Complete Interview Flow")
    print("=" * 50)
    
    # 1. Check environment variables
    print("1️⃣ Checking environment variables...")
    google_key = os.getenv("GOOGLE_API_KEY")
    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_key = os.getenv("LIVEKIT_API_KEY")
    livekit_secret = os.getenv("LIVEKIT_API_SECRET")
    
    if not google_key:
        print("❌ GOOGLE_API_KEY not found")
        return
    if not livekit_url:
        print("❌ LIVEKIT_URL not found")
        return
    if not livekit_key:
        print("❌ LIVEKIT_API_KEY not found")
        return
    if not livekit_secret:
        print("❌ LIVEKIT_API_SECRET not found")
        return
    
    print(f"✅ Google API Key: {google_key[:8]}...")
    print(f"✅ LiveKit URL: {livekit_url}")
    print(f"✅ LiveKit Key: {livekit_key}")
    print()
    
    # 2. Test LiveKit server connection
    print("2️⃣ Testing LiveKit server connection...")
    try:
        import requests
        # Test if LiveKit server is accessible
        response = requests.get("http://localhost:7880", timeout=5)
        print("✅ LiveKit server is accessible")
    except Exception as e:
        print(f"❌ LiveKit server connection failed: {e}")
        print("💡 Make sure to run: cd docker && docker-compose up -d")
        return
    
    # 3. Test database creation
    print("3️⃣ Testing database setup...")
    try:
        import sqlite3
        db_path = "database/interview_sessions.db"
        os.makedirs("database", exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.close()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return
    
    # 4. Test agent imports
    print("4️⃣ Testing agent imports...")
    try:
        from core.pure_livekit_interview_agent import InterviewAgent
        from core.interview_tools import generate_interview_questions
        from core.interview_prompts import INTERVIEWER_INSTRUCTION
        print("✅ All agent components imported successfully")
    except Exception as e:
        print(f"❌ Agent import failed: {e}")
        return
    
    # 5. Generate test token
    print("5️⃣ Generating test room token...")
    try:
        from livekit import api
        
        # Create room token
        token = api.AccessToken(livekit_key, livekit_secret) \
            .with_identity("test_candidate") \
            .with_name("Test Candidate") \
            .with_grants(api.VideoGrants(
                room_join=True,
                room="interview_test_room",
                can_publish=True,
                can_subscribe=True,
            )) \
            .to_jwt()
        
        web_url = f"http://localhost:3000?token={token}&url={livekit_url}"
        
        print("✅ Test token generated successfully")
        print(f"🌐 Test URL: {web_url}")
        print()
        
    except Exception as e:
        print(f"❌ Token generation failed: {e}")
        return
    
    print("🎉 ALL TESTS PASSED!")
    print()
    print("🚀 READY TO START INTERVIEW FLOW:")
    print("1. Run the agent: python core/pure_livekit_interview_agent.py dev")
    print("2. Use the test URL above to join as a candidate")
    print("3. The agent should greet you and start the interview")
    print()
    print("📊 Monitor the interview:")
    print("- Agent logs will show in the terminal")
    print("- Database entries: python utils/view_database.py")
    print()

if __name__ == "__main__":
    asyncio.run(test_complete_flow())
