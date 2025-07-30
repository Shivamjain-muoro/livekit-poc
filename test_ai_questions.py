"""
Test AI question generation with detailed debugging
"""
import requests
import json
import time

def test_ai_question_generation():
    print("🔍 Testing AI Question Generation...")
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test session creation to trigger AI question generation
        print("📋 Creating session to test AI question generation...")
        response = requests.post('http://localhost:8000/api/interview/create-session', 
            json={
                "candidate": {
                    "name": "AI Test User",
                    "email": "aitest@example.com",
                    "position": "Python Developer",
                    "experience_level": "senior",  # Use senior to get different questions
                    "skills": ["Python", "Django", "Machine Learning", "AWS"]
                }
            },
            timeout=15  # Longer timeout for AI generation
        )
        
        if response.status_code != 200:
            print(f"❌ Session creation failed: {response.status_code}")
            print(response.text)
            return
            
        data = response.json()
        
        print("✅ Session creation successful!")
        print()
        print("🎯 Questions in Response:")
        
        questions = data.get('questions', [])
        if questions:
            print(f"   Found {len(questions)} questions:")
            for i, q in enumerate(questions, 1):
                print(f"   {i}. {q}")
            
            # Check if these look like AI-generated or fallback questions
            print()
            print("🔍 Question Analysis:")
            ai_indicators = ["Python", "Django", "Machine Learning", "AWS", "senior"]
            fallback_indicators = ["microservices", "concurrent users", "design patterns"]
            
            questions_text = " ".join(questions).lower()
            
            ai_score = sum(1 for indicator in ai_indicators if indicator.lower() in questions_text)
            fallback_score = sum(1 for indicator in fallback_indicators if indicator.lower() in questions_text)
            
            if ai_score > fallback_score:
                print("   ✅ Questions appear to be AI-generated (contain skill-specific content)")
            else:
                print("   ⚠️ Questions appear to be fallback/predefined questions")
                
            print(f"   AI indicators found: {ai_score}")
            print(f"   Fallback indicators found: {fallback_score}")
        else:
            print("   ❌ No questions found in response!")
        
        print()
        print("📊 Full Response:")
        print(f"   session_id: {data.get('session_id')}")
        print(f"   ai_enabled: {data.get('ai_enabled')}")
        print(f"   status: {data.get('status')}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server at http://localhost:8000")
        print("   Make sure the server is running!")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_ai_question_generation()
