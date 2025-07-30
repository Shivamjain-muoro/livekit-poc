"""
Test the complete interview flow including feedback endpoint
"""
import requests
import json
import time

def test_complete_interview_flow():
    print("🎯 Testing Complete Interview Flow with Feedback...")
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Step 1: Create session
        print("Step 1: Creating interview session...")
        session_response = requests.post('http://localhost:8000/api/interview/create-session', 
            json={
                "candidate": {
                    "name": "Test Candidate",
                    "email": "test@example.com",
                    "position": "Python Developer",
                    "experience_level": "mid",
                    "skills": ["Python", "Django", "REST APIs"]
                }
            },
            timeout=10
        )
        
        if session_response.status_code != 200:
            print(f"❌ Session creation failed: {session_response.status_code}")
            return
            
        session_data = session_response.json()
        session_id = session_data['session_id']
        print(f"✅ Session created: {session_id}")
        
        # Step 2: Start interview
        print("Step 2: Starting interview...")
        start_response = requests.post('http://localhost:8000/api/interview/start',
            json={"session_id": session_id},
            timeout=10
        )
        
        if start_response.status_code != 200:
            print(f"❌ Start interview failed: {start_response.status_code}")
            return
            
        print("✅ Interview started")
        
        # Step 3: Submit a few answers
        print("Step 3: Submitting answers...")
        for i in range(3):  # Submit 3 answers
            submit_response = requests.post('http://localhost:8000/api/interview/submit-answer',
                json={
                    "session_id": session_id,
                    "question_id": f"q_{i+1}",
                    "answer_text": f"This is my detailed answer to question {i+1}. I have experience with the technologies mentioned and can provide specific examples of how I've used them in real projects.",
                    "duration": 45
                },
                timeout=10
            )
            
            if submit_response.status_code != 200:
                print(f"❌ Submit answer {i+1} failed: {submit_response.status_code}")
                return
                
            result = submit_response.json()
            print(f"✅ Answer {i+1} submitted - Complete: {result.get('is_complete', False)}")
            
            if result.get('is_complete'):
                break
        
        # Step 4: Test feedback endpoint
        print("Step 4: Getting interview feedback...")
        feedback_response = requests.get(f'http://localhost:8000/api/interview/feedback/{session_id}',
            timeout=10
        )
        
        if feedback_response.status_code != 200:
            print(f"❌ Feedback request failed: {feedback_response.status_code}")
            print(feedback_response.text)
            return
            
        feedback_data = feedback_response.json()
        print("✅ Feedback retrieved successfully!")
        
        # Display feedback summary
        print()
        print("🎉 INTERVIEW FEEDBACK SUMMARY:")
        print(f"   Candidate: {feedback_data.get('candidate_name')}")
        print(f"   Position: {feedback_data.get('position')}")
        print(f"   Overall Score: {feedback_data.get('overall_score', 0):.1f}%")
        print(f"   Questions Answered: {feedback_data.get('answers_submitted', 0)}/{feedback_data.get('total_questions', 0)}")
        print(f"   Recommendation: {feedback_data.get('recommendation', 'N/A')}")
        
        strengths = feedback_data.get('strengths', [])
        if strengths:
            print(f"   Strengths: {', '.join(strengths[:3])}")
            
        improvements = feedback_data.get('improvements', [])
        if improvements:
            print(f"   Improvements: {', '.join(improvements[:3])}")
        
        print()
        print("✅ Complete interview flow working successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server at http://localhost:8000")
        print("   Make sure the server is running!")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_complete_interview_flow()
