"""
Enhanced AI Interview System Backend with Local LiveKit
=====================================================
Complete FastAPI backend with local LiveKit server integration.
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

# Import our models and managers
from models.interview_models import (
    Candidate, SessionCreateRequest, SessionResponse, 
    StartInterviewRequest, StartInterviewResponse,
    SubmitAnswerRequest, SubmitAnswerResponse,
    JoinSessionRequest, JoinSessionResponse,
    ExperienceLevel
)
from interview.manager import InterviewManager

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Local LiveKit configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced AI Interview System with Local LiveKit",
    description="Complete AI-powered interview platform with local LiveKit server",
    version="2.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files for local LiveKit client
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize interview manager
interview_manager = InterviewManager()

# Basic health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Enhanced AI Interview System with Local LiveKit",
        "version": "2.1.0",
        "livekit_url": LIVEKIT_URL,
        "timestamp": datetime.now().isoformat()
    }

# Serve main demo interface
@app.get("/", response_class=HTMLResponse)
async def serve_main_interface():
    """Serve the main demo interface"""
    html_content = f"""
    <!DOCTYPE html>
    <html><head><title>AI Interview System - Local LiveKit</title></head>
    <body>
        <h1>🎯 AI Interview System Backend (Local LiveKit)</h1>
        <p>Enhanced backend with local LiveKit server is running!</p>
        <h2>Available Interfaces:</h2>
        <ul>
            <li><a href="/live-local">Live Interview (Local LiveKit)</a></li>
            <li><a href="/live-fixed">Live Interview (CDN Fallback)</a></li>
            <li><a href="/simple">Simple Voice Interview</a></li>
            <li><a href="/voice-only">Voice-Only Interview (No LiveKit)</a></li>
            <li><a href="/docs">API Documentation</a></li>
        </ul>
        <h3>LiveKit Server Status:</h3>
        <p>URL: {LIVEKIT_URL}</p>
        <p>API Key: {LIVEKIT_API_KEY}</p>
    </body></html>
    """
    return HTMLResponse(content=html_content)

# Serve local LiveKit interview interface
@app.get("/live-local", response_class=HTMLResponse)
async def serve_local_live_interview():
    """Serve the local LiveKit interview interface"""
    try:
        with open("live_interview_local.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Local LiveKit interview interface not found</h1>")

# Serve fixed live interview interface (CDN fallback)
@app.get("/live-fixed", response_class=HTMLResponse)
async def serve_live_interview_fixed():
    """Serve the fixed live video interview interface with CDN"""
    try:
        with open("live_interview_fixed.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Fixed live interview interface not found</h1>")

# Serve simple interview interface
@app.get("/simple", response_class=HTMLResponse)
async def serve_simple_interview():
    """Serve the simple interview interface without LiveKit"""
    try:
        with open("simple_interview.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Simple interview interface not found</h1>")

# Serve voice-only interview interface
@app.get("/voice-only", response_class=HTMLResponse)
async def serve_voice_only_interview():
    """Serve the voice-only interview interface"""
    try:
        with open("live_interview_no_livekit.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Voice-only interview interface not found</h1>")

# Create interview session with LiveKit tokens
@app.post("/api/interview/create-session", response_model=SessionResponse)
async def create_interview_session(request: SessionCreateRequest):
    """Create a new interview session with LiveKit tokens"""
    try:
        session = await interview_manager.create_session(
            candidate=request.candidate
        )
        
        # Generate LiveKit tokens for local server
        participant_token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        participant_token.with_identity(f"participant-{session.id}")
        participant_token.with_name(session.candidate.name)
        participant_grants = VideoGrants(room_join=True, room=session.room_name)
        participant_token.with_grants(participant_grants)
        
        agent_token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        agent_token.with_identity(f"agent-{session.id}")
        agent_token.with_name("AI Interviewer")
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

@app.post("/api/interview/start", response_model=StartInterviewResponse)
async def start_interview(request: StartInterviewRequest):
    """Start an interview session"""
    try:
        first_question = interview_manager.start_interview(request.session_id)
        return StartInterviewResponse(
            success=True,
            message="Interview started successfully",
            first_question=first_question
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")

@app.post("/api/interview/submit-answer", response_model=SubmitAnswerResponse)
async def submit_answer(request: SubmitAnswerRequest):
    """Submit an answer to a question"""
    try:
        feedback, next_question, is_complete = await interview_manager.submit_answer(
            session_id=request.session_id,
            question_id=request.question_id,
            answer_text=request.answer_text,
            audio_duration=request.audio_duration
        )
        return SubmitAnswerResponse(
            success=True,
            message="Answer submitted successfully",
            next_question=next_question,
            interview_complete=is_complete
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit answer: {str(e)}")

@app.get("/api/interview/feedback/{session_id}")
async def get_interview_feedback(session_id: str):
    """Get feedback for a completed interview"""
    try:
        feedback = interview_manager.generate_interview_summary(session_id)
        return feedback
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feedback: {str(e)}")

@app.get("/api/interview/sessions")
async def list_sessions():
    """List all interview sessions"""
    try:
        sessions = interview_manager.list_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced AI Interview System with Local LiveKit...")
    print("=" * 60)
    print(f"🌐 API Server: http://localhost:8002")
    print(f"🎯 Demo Frontend: http://localhost:8002")
    print(f"🏠 Live Interview (Local): http://localhost:8002/live-local")
    print(f"🔧 Live Interview (CDN): http://localhost:8002/live-fixed") 
    print(f"📝 Simple Interview: http://localhost:8002/simple")
    print(f"🎤 Voice-Only Interview: http://localhost:8002/voice-only")
    print(f"📊 Health Check: http://localhost:8002/health")
    print(f"📚 API Docs: http://localhost:8002/docs")
    print(f"🔧 Admin Panel: http://localhost:8002/api/interview/sessions")
    print("=" * 60)
    print(f"🔴 LiveKit Server: {LIVEKIT_URL}")
    print(f"🔑 API Key: {LIVEKIT_API_KEY}")
    print("=" * 60)
    
    uvicorn.run(
        "enhanced_backend:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
