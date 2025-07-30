"""
Simplified Enhanced Backend without LLM dependencies for testing
"""
import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from livekit.api import AccessToken
from livekit.api.access_token import VideoGrants
from datetime import datetime
import uvicorn

# Import our models
from models.interview_models import (
    Candidate, SessionCreateRequest, SessionResponse, 
    StartInterviewRequest, StartInterviewResponse,
    SubmitAnswerRequest, SubmitAnswerResponse,
    JoinSessionRequest, JoinSessionResponse,
    ExperienceLevel, Question, QuestionType, Feedback
)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# FastAPI app
app = FastAPI(title="AI Interview System - Enhanced Backend", version="2.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# LiveKit configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")

# Simple in-memory storage for demo
sessions = {}
questions_db = {
    "technical": [
        "Explain the difference between synchronous and asynchronous programming.",
        "What is the time complexity of binary search?",
        "How does garbage collection work in programming languages?",
        "Explain the concept of RESTful APIs.",
        "What are the benefits of using version control systems?"
    ],
    "behavioral": [
        "Tell me about a challenging project you worked on.",
        "How do you handle tight deadlines?",
        "Describe a time you had to learn a new technology quickly.",
        "How do you prioritize tasks when everything seems urgent?",
        "Tell me about a time you disagreed with a team member."
    ]
}

@app.get("/")
async def root():
    return {"message": "Enhanced AI Interview System Backend", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Serve HTML files
@app.get("/live-local")
async def serve_live_local():
    return FileResponse("live_interview_local.html")

@app.get("/simple")
async def serve_simple():
    return FileResponse("simple_interview.html")

@app.get("/voice-only")
async def serve_voice_only():
    return FileResponse("live_interview_no_livekit.html")

@app.get("/live-fixed")
async def serve_live_fixed():
    return FileResponse("live_interview_fixed.html")

# Create interview session with LiveKit tokens
@app.post("/api/interview/create-session", response_model=SessionResponse)
async def create_interview_session(request: SessionCreateRequest):
    """Create a new interview session with LiveKit tokens"""
    try:
        # Generate session ID
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        room_name = f"interview_{session_id}"
        
        # Generate LiveKit tokens for local server
        participant_token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        participant_token.with_identity(f"participant-{session_id}")
        participant_token.with_name(request.candidate.name)
        participant_grants = VideoGrants(room_join=True, room=room_name)
        participant_token.with_grants(participant_grants)
        
        agent_token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        agent_token.with_identity(f"agent-{session_id}")
        agent_token.with_name("AI Interviewer")
        agent_grants = VideoGrants(room_join=True, room=room_name)
        agent_token.with_grants(agent_grants)
        
        # Store session info
        sessions[session_id] = {
            "id": session_id,
            "candidate": request.candidate,
            "room_name": room_name,
            "status": "created",
            "created_at": datetime.now(),
            "current_question_index": 0,
            "questions": [],
            "answers": []
        }
        
        return SessionResponse(
            session_id=session_id,
            room_name=room_name,
            participant_token=participant_token.to_jwt(),
            agent_token=agent_token.to_jwt(),
            livekit_url=LIVEKIT_URL,
            status="created"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.post("/api/interview/start", response_model=StartInterviewResponse)
async def start_interview(request: StartInterviewRequest):
    """Start an interview session"""
    try:
        if request.session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = sessions[request.session_id]
        session["status"] = "started"
        session["start_time"] = datetime.now()
        
        # Generate simple questions based on position
        position = session["candidate"].position.lower()
        question_type = "technical" if any(word in position for word in ["engineer", "developer", "programmer"]) else "behavioral"
        
        # Create first question
        first_question = Question(
            id=f"q_{uuid.uuid4().hex[:8]}",
            session_id=request.session_id,
            question_text=questions_db[question_type][0],
            question_type=QuestionType.TECHNICAL if question_type == "technical" else QuestionType.BEHAVIORAL,
            difficulty_level=2,
            expected_duration=120,
            order_index=1,
            is_asked=True,
            asked_at=datetime.now()
        )
        
        session["questions"].append(first_question)
        session["current_question_index"] = 1
        
        return StartInterviewResponse(
            success=True,
            first_question=first_question,
            total_questions=5,
            estimated_duration=15  # 15 minutes total
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")

@app.post("/api/interview/submit-answer", response_model=SubmitAnswerResponse)
async def submit_answer(request: SubmitAnswerRequest):
    """Submit an answer to a question"""
    try:
        if request.session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = sessions[request.session_id]
        
        # Store the answer
        answer = {
            "id": f"a_{uuid.uuid4().hex[:8]}",
            "session_id": request.session_id,
            "question_id": request.question_id,
            "answer_text": request.answer_text,
            "duration": request.duration,
            "submitted_at": datetime.now()
        }
        session["answers"].append(answer)
        
        # Check if interview is complete (5 questions)
        is_complete = session["current_question_index"] >= 5
        next_question = None
        
        if not is_complete:
            # Generate next question
            question_index = session["current_question_index"]
            candidate = session["candidate"]
            position = candidate.position.lower()
            question_type = "technical" if any(word in position for word in ["engineer", "developer", "programmer"]) else "behavioral"
            
            if question_index < len(questions_db[question_type]):
                next_question = Question(
                    id=f"q_{uuid.uuid4().hex[:8]}",
                    session_id=request.session_id,
                    question_text=questions_db[question_type][question_index],
                    question_type=QuestionType.TECHNICAL if question_type == "technical" else QuestionType.BEHAVIORAL,
                    difficulty_level=2,
                    expected_duration=120,
                    order_index=question_index + 1,
                    is_asked=True,
                    asked_at=datetime.now()
                )
                session["questions"].append(next_question)
                session["current_question_index"] += 1
            else:
                is_complete = True
        
        # Create simple feedback for the answer
        simple_feedback = Feedback(
            id=f"f_{uuid.uuid4().hex[:8]}",
            answer_id=answer["id"],
            session_id=request.session_id,
            score=75,  # Simple score
            feedback_text="Good answer! You demonstrated understanding of the topic.",
            criteria_scores={"clarity": 4, "completeness": 3, "accuracy": 4},
            strengths=["Clear explanation", "Good examples"],
            improvements=["Consider adding more detail"],
            evaluated_at=datetime.now()
        )
        
        if is_complete:
            session["status"] = "completed"
            session["end_time"] = datetime.now()
        
        return SubmitAnswerResponse(
            success=True,
            feedback=simple_feedback,
            next_question=next_question,
            is_complete=is_complete
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit answer: {str(e)}")

@app.get("/api/interview/feedback/{session_id}")
async def get_interview_feedback(session_id: str):
    """Get feedback for a completed interview"""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = sessions[session_id]
        
        # Generate simple feedback
        num_answers = len(session["answers"])
        overall_score = min(90, 60 + (num_answers * 5))  # Simple scoring
        
        feedback = {
            "session_id": session_id,
            "candidate_name": session["candidate"].name,
            "position": session["candidate"].position,
            "overall_score": overall_score,
            "total_questions": len(session["questions"]),
            "total_answers": num_answers,
            "detailed_feedback": f"Great job completing the interview! You answered {num_answers} questions with confidence. Your responses showed good understanding of the topics discussed.",
            "strengths": ["Clear communication", "Technical knowledge", "Problem-solving approach"],
            "improvements": ["Consider providing more specific examples", "Practice explaining complex concepts"],
            "generated_at": datetime.now()
        }
        
        return feedback
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feedback: {str(e)}")

@app.get("/api/interview/sessions")
async def list_sessions():
    """List all interview sessions"""
    try:
        session_list = []
        for session_id, session in sessions.items():
            session_info = {
                "id": session_id,
                "candidate_name": session["candidate"].name,
                "position": session["candidate"].position,
                "status": session["status"],
                "created_at": session["created_at"],
                "questions_count": len(session["questions"]),
                "answers_count": len(session["answers"])
            }
            session_list.append(session_info)
        
        return {"sessions": session_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Simplified Enhanced AI Interview System...")
    print(f"🎯 LiveKit Server: {LIVEKIT_URL}")
    print(f"🔑 API Key: {LIVEKIT_API_KEY}")
    print(f"📱 Local Interview: http://localhost:8002/live-local")
    print(f"📊 Health Check: http://localhost:8002/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)
