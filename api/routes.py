import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from livekit.api import AccessToken
from livekit.api.access_token import VideoGrants
from datetime import datetime

# Import our models and managers
from models.interview_models import (
    Candidate, SessionCreateRequest, SessionResponse, 
    StartInterviewRequest, StartInterviewResponse,
    SubmitAnswerRequest, SubmitAnswerResponse,
    JoinSessionRequest, JoinSessionResponse
)
from interview.manager import InterviewManager

app = FastAPI(
    title="AI Interview System API",
    description="Backend API for AI-powered interview platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://testpoc-mys8x433.livekit.cloud")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

# Initialize interview manager
interview_manager = InterviewManager()

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "AI Interview System is running",
        "timestamp": datetime.now().isoformat()
    }

# Create interview session
@app.post("/api/interview/create", response_model=SessionResponse)
async def create_interview_session(request: SessionCreateRequest):
    """Create a new interview session with LiveKit tokens"""
    try:
        # Create session with generated questions
        session = await interview_manager.create_session(
            candidate=request.candidate,
            interview_type=request.interview_type
        )
        
        # Generate LiveKit tokens
        if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
            raise HTTPException(status_code=500, detail="LiveKit credentials not configured")
        
        # Participant token
        participant_token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        participant_token.with_identity(f"participant-{session.id}")
        participant_token.with_name(session.candidate.name)
        participant_grants = VideoGrants(room_join=True, room=session.room_name)
        participant_token.with_grants(participant_grants)
        
        # Agent token
        agent_token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        agent_token.with_identity(f"agent-{session.id}")
        agent_token.with_name("AI Interviewer Friday")
        agent_grants = VideoGrants(room_join=True, room=session.room_name, agent=True)
        agent_token.with_grants(agent_grants)
        
        return SessionResponse(
            session_id=session.id,
            room_name=session.room_name,
            participant_token=participant_token.to_jwt(),
            agent_token=agent_token.to_jwt(),
            livekit_url=LIVEKIT_URL,
            status=session.status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

# Join existing session
@app.post("/api/interview/join/{session_id}", response_model=JoinSessionResponse)
async def join_interview_session(session_id: str, request: JoinSessionRequest):
    """Join an existing interview session"""
    try:
        session = interview_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Generate new access token
        if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
            raise HTTPException(status_code=500, detail="LiveKit credentials not configured")
        
        participant_token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        participant_token.with_identity(f"participant-{session_id}")
        participant_token.with_name(request.participant_name or session.candidate.name)
        participant_grants = VideoGrants(room_join=True, room=session.room_name)
        participant_token.with_grants(participant_grants)
        
        return JoinSessionResponse(
            success=True,
            access_token=participant_token.to_jwt(),
            livekit_url=LIVEKIT_URL,
            room_name=session.room_name,
            session_status=session.status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to join session: {str(e)}")

# Start interview
@app.post("/api/interview/start/{session_id}", response_model=StartInterviewResponse)
async def start_interview(session_id: str):
    """Start the interview and return the first question"""
    try:
        session = interview_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        first_question = interview_manager.start_interview(session_id)
        if not first_question:
            raise HTTPException(status_code=500, detail="Failed to start interview")
        
        # Calculate estimated duration
        questions = interview_manager.get_session_questions(session_id)
        estimated_duration = sum(q.expected_duration for q in questions) // 60  # in minutes
        
        return StartInterviewResponse(
            success=True,
            first_question=first_question,
            total_questions=session.total_questions,
            estimated_duration=estimated_duration
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")

# Submit answer
@app.post("/api/interview/answer/{session_id}", response_model=SubmitAnswerResponse)
async def submit_answer(session_id: str, request: SubmitAnswerRequest):
    """Submit answer and get evaluation + next question"""
    try:
        feedback, next_question, is_complete = await interview_manager.submit_answer(
            session_id=session_id,
            question_id=request.question_id,
            answer_text=request.answer_text,
            duration=request.duration
        )
        
        session_summary = None
        if is_complete:
            session_summary = interview_manager.generate_interview_summary(session_id)
        
        return SubmitAnswerResponse(
            success=True,
            feedback=feedback,
            next_question=next_question,
            is_complete=is_complete,
            session_summary=session_summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit answer: {str(e)}")

# Get session details
@app.get("/api/interview/session/{session_id}")
async def get_session_details(session_id: str):
    """Get session details including current status"""
    try:
        session = interview_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        questions = interview_manager.get_session_questions(session_id)
        
        return {
            "session": session,
            "questions": questions,
            "progress": {
                "current_question": session.current_question_index,
                "total_questions": session.total_questions,
                "percentage": (session.current_question_index / session.total_questions * 100) if session.total_questions > 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

# Get interview summary
@app.get("/api/interview/summary/{session_id}")
async def get_interview_summary(session_id: str):
    """Get final interview summary and evaluation"""
    try:
        summary = interview_manager.generate_interview_summary(session_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Summary not found or interview not complete")
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")
