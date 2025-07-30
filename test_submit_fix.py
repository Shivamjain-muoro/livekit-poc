"""
Quick test for submit answer API to verify the audio_duration fix
"""
import requests
import json
import time

def test_submit_answer_fix():
    print("🔍 Testing Submit Answer API Fix...")
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Step 1: Create a session first
        print("Step 1: Creating session...")
        session_response = requests.post('http://localhost:8000/api/interview/create-session', 
            json={
                "candidate": {
                    "name": "Test User",
                    "email": "test@example.com",
                    "position": "Software Engineer",
                    "experience_level": "mid",
                    "skills": ["Python"]
                }
            },
            timeout=10
        )
        
        if session_response.status_code != 200:
            print(f"❌ Session creation failed: {session_response.status_code}")
            print(session_response.text)
            return False
            
        session_data = session_response.json()
        session_id = session_data['session_id']
        print(f"✅ Session created: {session_id}")
        
        # Step 2: Start the interview
        print("Step 2: Starting interview...")
        start_response = requests.post('http://localhost:8000/api/interview/start',
            json={"session_id": session_id},
            timeout=10
        )
        
        if start_response.status_code != 200:
            print(f"❌ Start interview failed: {start_response.status_code}")
            print(start_response.text)
            return False
            
        print("✅ Interview started")
        
        # Step 3: Test submit answer with the FIXED field name
        print("Step 3: Testing submit answer with correct field name...")
        submit_response = requests.post('http://localhost:8000/api/interview/submit-answer',
            json={
                "session_id": session_id,
                "question_id": "q_1",
                "answer_text": "This is my test answer for the interview question.",
                "duration": 30  # This should now work (was audio_duration)
            },
            timeout=10
        )
        
        if submit_response.status_code != 200:
            print(f"❌ Submit answer failed: {submit_response.status_code}")
            print(submit_response.text)
            return False
            
        result = submit_response.json()
        print("✅ Submit answer successful!")
        print(f"   Success: {result.get('success')}")
        print(f"   Is Complete: {result.get('is_complete')}")
        print(f"   Has Feedback: {'feedback' in result}")
        print(f"   Has Next Question: {result.get('next_question') is not None}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server at http://localhost:8000")
        print("   Make sure the server is running!")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    if test_submit_answer_fix():
        print("\n🎉 All API endpoints working correctly!")
        print("\n📝 Ready for complete UI testing:")
        print("   Open: http://localhost:8000/live-local")
        print("   Fill form and start interview")
        print("   Submit answers should now work without errors!")
    else:
        print("\n⚠️ API still has issues. Check server logs for details.")
