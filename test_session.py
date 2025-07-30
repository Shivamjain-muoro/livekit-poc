import requests
import json

data = {
    'candidate': {
        'name': 'Test User',
        'email': 'test@example.com',
        'position': 'Software Engineer',
        'experience_level': 'mid',  # Changed to lowercase
        'skills': ['Python', 'JavaScript']
    }
}

try:
    response = requests.post('http://localhost:8003/api/interview/create-session', 
                           json=data, 
                           headers={'Content-Type': 'application/json'})
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.text}')
except Exception as e:
    print(f'Error: {e}')
