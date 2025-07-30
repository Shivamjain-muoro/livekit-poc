"""
Test to verify session creation returns questions correctly
"""
import requests
import json

def test_session_creation_questions():
    print("🔍 Testing Session Creation - Questions Response...")
    
    try:
        # Create a session
        response = requests.post('http://localhost:8000/api/interview/create-session', 
            json={
                "candidate": {
                    "name": "Test User",
                    "email": "test@example.com",
                    "position": "Software Engineer",
                    "experience_level": "mid",
                    "skills": ["Python", "JavaScript"]
                }
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Session creation failed: {response.status_code}")
            print(response.text)
            return
            
        data = response.json()
        
        print("✅ Session creation successful!")
        print(f"📋 Response keys: {list(data.keys())}")
        print()
        
        # Check each field
        print("📊 Session Response Details:")
        print(f"   session_id: {data.get('session_id', 'MISSING')}")
        print(f"   room_name: {data.get('room_name', 'MISSING')}")
        print(f"   participant_token: {'✅ Present' if data.get('participant_token') else '❌ Missing'}")
        print(f"   agent_token: {'✅ Present' if data.get('agent_token') else '❌ Missing'}")
        print(f"   livekit_url: {data.get('livekit_url', 'MISSING')}")
        print(f"   status: {data.get('status', 'MISSING')}")
        print(f"   ai_enabled: {data.get('ai_enabled', 'MISSING')}")
        
        # Most importantly - check questions
        questions = data.get('questions')
        print()
        print("🎯 QUESTIONS CHECK:")
        if questions is None:
            print("   ❌ 'questions' field is missing from response!")
        elif not questions:
            print("   ❌ 'questions' field is empty!")
        else:
            print(f"   ✅ Found {len(questions)} questions:")
            for i, q in enumerate(questions, 1):
                print(f"      {i}. {q}")
        
        print()
        print("🔍 Full Response JSON:")
        print(json.dumps(data, indent=2))
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server at http://localhost:8000")
        print("   Make sure the server is running!")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_session_creation_questions()
