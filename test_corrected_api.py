import requests
import json

# Test session creation
print("Testing session creation...")
session_data = {
    'candidate': {
        'name': 'Test User',
        'email': 'test@example.com',
        'position': 'Software Engineer',
        'experience_level': 'mid',
        'skills': ['Python', 'JavaScript']
    }
}

response = requests.post('http://localhost:8002/api/interview/create-session', 
                       json=session_data, 
                       headers={'Content-Type': 'application/json'})
print(f'Session Creation - Status: {response.status_code}')
if response.status_code == 200:
    session_response = response.json()
    session_id = session_response['session_id']
    print(f'Session ID: {session_id}')
    
    # Test interview start
    print("\nTesting interview start...")
    start_data = {'session_id': session_id}
    start_response = requests.post('http://localhost:8002/api/interview/start',
                                 json=start_data,
                                 headers={'Content-Type': 'application/json'})
    print(f'Interview Start - Status: {start_response.status_code}')
    if start_response.status_code == 200:
        start_result = start_response.json()
        print(f'Success: {start_result["success"]}')
        print(f'Total Questions: {start_result["total_questions"]}')
        print(f'Estimated Duration: {start_result["estimated_duration"]} minutes')
        print(f'First Question: {start_result["first_question"]["question_text"]}')
    else:
        print(f'Error: {start_response.text}')
else:
    print(f'Error: {response.text}')
