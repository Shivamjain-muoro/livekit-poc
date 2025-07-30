import requests
import json

# Test the corrected submit answer API
print("Testing submit answer API with corrected field names...")

# First create a session
session_data = {
    'candidate': {
        'name': 'Test User',
        'email': 'test@example.com',
        'position': 'Software Engineer',
        'experience_level': 'mid',
        'skills': ['Python', 'JavaScript']
    }
}

# Create session
session_response = requests.post('http://localhost:8002/api/interview/create-session', 
                               json=session_data, 
                               headers={'Content-Type': 'application/json'})

if session_response.status_code == 200:
    session_result = session_response.json()
    session_id = session_result['session_id']
    print(f'Session created: {session_id}')
    
    # Start interview
    start_response = requests.post('http://localhost:8002/api/interview/start',
                                 json={'session_id': session_id},
                                 headers={'Content-Type': 'application/json'})
    
    if start_response.status_code == 200:
        start_result = start_response.json()
        question_id = start_result['first_question']['id']
        print(f'Interview started, first question ID: {question_id}')
        
        # Test submit answer with corrected field names
        answer_data = {
            'session_id': session_id,
            'question_id': question_id,
            'answer_text': 'This is my test answer',
            'duration': 30  # Using 'duration' instead of 'audio_duration'
        }
        
        answer_response = requests.post('http://localhost:8002/api/interview/submit-answer',
                                      json=answer_data,
                                      headers={'Content-Type': 'application/json'})
        
        print(f'Submit Answer - Status: {answer_response.status_code}')
        if answer_response.status_code == 200:
            answer_result = answer_response.json()
            print(f'Success: {answer_result["success"]}')
            print(f'Is Complete: {answer_result["is_complete"]}')
            if answer_result.get("next_question"):
                print(f'Next Question: {answer_result["next_question"]["question_text"]}')
        else:
            print(f'Error: {answer_response.text}')
    else:
        print(f'Start interview failed: {start_response.text}')
else:
    print(f'Session creation failed: {session_response.text}')
