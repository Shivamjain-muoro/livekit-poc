# AI Interview System - API Testing Guide

## Overview
This guide provides comprehensive examples for testing the AI Interview System API endpoints using curl, Postman, or any HTTP client.

## Base URL
```
http://localhost:8002
```

## Authentication
No authentication required for demo purposes. In production, add JWT/OAuth.

## Core API Endpoints

### 1. Health Check
**GET** `/health`

```bash
curl -X GET "http://localhost:8002/health"
```

**Response:**
```json
{
  "status": "healthy",
  "message": "AI Interview System is running",
  "timestamp": "2025-07-30T16:10:33.333460",
  "livekit_configured": false
}
```

### 2. Create Interview Session
**POST** `/api/interview/create`

```bash
curl -X POST "http://localhost:8002/api/interview/create" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "John Doe",
      "email": "john.doe@example.com",
      "position": "Software Engineer",
      "experience_level": "mid",
      "skills": ["Python", "JavaScript", "React"]
    },
    "interview_type": "technical"
  }'
```

**Response:**
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "room_name": "interview-a1b2c3d4",
  "participant_token": "eyJ...",
  "agent_token": "eyJ...",
  "livekit_url": "wss://testpoc-mys8x433.livekit.cloud",
  "status": "created"
}
```

### 3. Start Interview
**POST** `/api/interview/start/{session_id}`

```bash
curl -X POST "http://localhost:8002/api/interview/start/a1b2c3d4-e5f6-7890-1234-567890abcdef"
```

**Response:**
```json
{
  "success": true,
  "first_question": {
    "id": "q1a2b3c4-d5e6-7890-1234-567890abcdef",
    "session_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "question_text": "Tell me about your experience with Software Engineer roles.",
    "question_type": "behavioral",
    "difficulty_level": 2,
    "expected_duration": 120,
    "order_index": 1,
    "is_asked": true,
    "asked_at": "2025-07-30T16:15:00"
  },
  "total_questions": 5,
  "estimated_duration": 12
}
```

### 4. Submit Answer
**POST** `/api/interview/answer/{session_id}`

```bash
curl -X POST "http://localhost:8002/api/interview/answer/a1b2c3d4-e5f6-7890-1234-567890abcdef" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "question_id": "q1a2b3c4-d5e6-7890-1234-567890abcdef",
    "answer_text": "I have 5 years of experience as a Software Engineer, working primarily with Python and JavaScript. I have built web applications using React and Django, and have experience with cloud platforms like AWS.",
    "duration": 145
  }'
```

**Response:**
```json
{
  "success": true,
  "feedback": {
    "id": "f1a2b3c4-d5e6-7890-1234-567890abcdef",
    "answer_id": "ans123",
    "session_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "score": 4,
    "feedback_text": "Good comprehensive answer with specific technology mentions and quantified experience.",
    "criteria_scores": {
      "technical_accuracy": 4,
      "communication": 4,
      "problem_solving": 4,
      "knowledge_depth": 4,
      "relevance": 4
    },
    "strengths": ["Specific technology experience", "Quantified experience"],
    "improvements": ["Could provide more specific examples"],
    "evaluated_at": "2025-07-30T16:18:00"
  },
  "next_question": {
    "id": "q2a2b3c4-d5e6-7890-1234-567890abcdef",
    "question_text": "Describe a challenging project you worked on and how you overcame obstacles.",
    "question_type": "behavioral",
    "difficulty_level": 3,
    "expected_duration": 180,
    "order_index": 2
  },
  "is_complete": false
}
```

### 5. Get Session Details
**GET** `/api/interview/session/{session_id}`

```bash
curl -X GET "http://localhost:8002/api/interview/session/a1b2c3d4-e5f6-7890-1234-567890abcdef"
```

**Response:**
```json
{
  "session": {
    "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "candidate": {
      "name": "John Doe",
      "email": "john.doe@example.com",
      "position": "Software Engineer",
      "experience_level": "mid"
    },
    "status": "in_progress",
    "current_question_index": 2,
    "total_questions": 5
  },
  "progress": {
    "current_question": 2,
    "total_questions": 5,
    "percentage": 40.0
  }
}
```

### 6. Get Interview Summary
**GET** `/api/interview/summary/{session_id}`

```bash
curl -X GET "http://localhost:8002/api/interview/summary/a1b2c3d4-e5f6-7890-1234-567890abcdef"
```

**Response:**
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "candidate_name": "John Doe",
  "position": "Software Engineer",
  "overall_score": 3.8,
  "total_duration": 720,
  "questions_asked": 5,
  "category_scores": {
    "technical": 4.0,
    "behavioral": 3.6
  },
  "strengths": [
    "Strong technical knowledge",
    "Clear communication",
    "Specific examples"
  ],
  "areas_for_improvement": [
    "Could provide more detailed explanations",
    "Consider discussing team collaboration more"
  ],
  "recommendation": "hire",
  "detailed_feedback": "Overall performance was good.",
  "generated_at": "2025-07-30T16:25:00"
}
```

### 7. Join Session (LiveKit)
**POST** `/api/interview/join/{session_id}`

```bash
curl -X POST "http://localhost:8002/api/interview/join/a1b2c3d4-e5f6-7890-1234-567890abcdef" \
  -H "Content-Type: application/json" \
  -d '{
    "participant_name": "John Doe"
  }'
```

**Response:**
```json
{
  "success": true,
  "access_token": "eyJ...",
  "livekit_url": "wss://testpoc-mys8x433.livekit.cloud",
  "room_name": "interview-a1b2c3d4",
  "session_status": "created"
}
```

## Admin/Debugging Endpoints

### 8. List All Sessions
**GET** `/api/interview/sessions`

```bash
curl -X GET "http://localhost:8002/api/interview/sessions"
```

### 9. Delete Session
**DELETE** `/api/interview/session/{session_id}`

```bash
curl -X DELETE "http://localhost:8002/api/interview/session/a1b2c3d4-e5f6-7890-1234-567890abcdef"
```

## Demo Data Endpoints

### 10. Get Demo Questions
**GET** `/api/demo/questions`

```bash
curl -X GET "http://localhost:8002/api/demo/questions"
```

### 11. Get Evaluation Criteria
**GET** `/api/demo/evaluation-criteria`

```bash
curl -X GET "http://localhost:8002/api/demo/evaluation-criteria"
```

## Complete Interview Flow Example

Here's a complete example of the interview flow:

```bash
# 1. Create session
SESSION_RESPONSE=$(curl -s -X POST "http://localhost:8002/api/interview/create" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Alice Smith",
      "email": "alice@example.com",
      "position": "Frontend Developer",
      "experience_level": "mid",
      "skills": ["React", "TypeScript", "CSS"]
    },
    "interview_type": "technical"
  }')

# Extract session ID
SESSION_ID=$(echo $SESSION_RESPONSE | jq -r '.session_id')
echo "Created session: $SESSION_ID"

# 2. Start interview
START_RESPONSE=$(curl -s -X POST "http://localhost:8002/api/interview/start/$SESSION_ID")
QUESTION_ID=$(echo $START_RESPONSE | jq -r '.first_question.id')
echo "First question ID: $QUESTION_ID"

# 3. Submit answer
ANSWER_RESPONSE=$(curl -s -X POST "http://localhost:8002/api/interview/answer/$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"question_id\": \"$QUESTION_ID\",
    \"answer_text\": \"I have 3 years of experience with React and TypeScript, building responsive web applications.\",
    \"duration\": 120
  }")

echo "Answer submitted. Score: $(echo $ANSWER_RESPONSE | jq -r '.feedback.score')"

# 4. Continue with next questions...
# Repeat step 3 for each question

# 5. Get final summary (after all questions are answered)
curl -s -X GET "http://localhost:8002/api/interview/summary/$SESSION_ID" | jq '.'
```

## Postman Collection

You can import these endpoints into Postman:

1. Create a new collection called "AI Interview System"
2. Add each endpoint as a new request
3. Set the base URL as `{{base_url}}` variable = `http://localhost:8002`
4. Use the session_id from create response in subsequent requests

## Error Handling

All endpoints return standard HTTP status codes:

- **200**: Success
- **400**: Bad Request (validation errors)
- **404**: Not Found (session/resource not found)
- **500**: Internal Server Error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

No rate limiting implemented in demo. In production, consider adding:
- Rate limiting per IP
- Request throttling for expensive operations
- API key authentication

## WebSocket Support

The system includes WebSocket support for real-time features:

```javascript
const ws = new WebSocket(`ws://localhost:8002/ws/${sessionId}`);
ws.onmessage = (event) => {
  console.log('Real-time update:', event.data);
};
```

This completes the API testing guide for the AI Interview System!
