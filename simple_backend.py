"""
LiveKit Interview Backend API - Simplified Version
===============================================
FastAPI backend for the LiveKit Interview System with essential functionality.
"""

import os
import json
import uuid
import asyncio
import sqlite3
from datetime import datetime
from typing import Optional, Dict, List
from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from livekit.api import AccessToken
from livekit.api.access_token import VideoGrants
import aiofiles

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://testpoc-mys8x433.livekit.cloud")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# FastAPI app
app = FastAPI(title="LiveKit Interview Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup - Simple SQLite for demo
def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect("interview_sessions.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            participant_name TEXT,
            participant_email TEXT,
            position TEXT,
            experience_level TEXT,
            room_name TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resume_content TEXT,
            interview_data TEXT
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

# Pydantic models
class CandidateInfo(BaseModel):
    name: str
    email: str
    position: str
    experience_level: str

class SessionCreateRequest(BaseModel):
    candidate: CandidateInfo
    interview_type: str = "technical"

class SessionResponse(BaseModel):
    session_id: str
    room_name: str
    participant_token: str
    agent_token: str
    livekit_url: str

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="LiveKit Interview Backend is running",
        timestamp=datetime.now().isoformat()
    )

# Session management
@app.post("/api/sessions", response_model=SessionResponse)
async def create_session(session_data: SessionCreateRequest):
    """Create a new interview session"""
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        room_name = f"interview-{session_id[:8]}"
        
        # Store session in database
        conn = sqlite3.connect("interview_sessions.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sessions (id, participant_name, participant_email, position, 
                                experience_level, room_name, interview_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            session_data.candidate.name,
            session_data.candidate.email,
            session_data.candidate.position,
            session_data.candidate.experience_level,
            room_name,
            json.dumps({"interview_type": session_data.interview_type})
        ))
        
        conn.commit()
        conn.close()
        
        # Generate LiveKit tokens
        if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
            raise HTTPException(status_code=500, detail="LiveKit credentials not configured")
        
        # Participant token
        participant_token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        participant_token.with_identity(f"participant-{session_id}")
        participant_token.with_name(session_data.candidate.name)
        participant_grants = VideoGrants(room_join=True, room=room_name)
        participant_token.with_grants(participant_grants)
        
        # Agent token
        agent_token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        agent_token.with_identity(f"agent-{session_id}")
        agent_token.with_name("AI Interviewer")
        agent_grants = VideoGrants(room_join=True, room=room_name, agent=True)
        agent_token.with_grants(agent_grants)
        
        return SessionResponse(
            session_id=session_id,
            room_name=room_name,
            participant_token=participant_token.to_jwt(),
            agent_token=agent_token.to_jwt(),
            livekit_url=LIVEKIT_URL
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    try:
        conn = sqlite3.connect("interview_sessions.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Session not found")
        
        columns = [description[0] for description in cursor.description]
        session_data = dict(zip(columns, row))
        
        return session_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@app.get("/api/sessions")
async def list_sessions():
    """List all sessions"""
    try:
        conn = sqlite3.connect("interview_sessions.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sessions ORDER BY created_at DESC LIMIT 50")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()
        
        sessions = [dict(zip(columns, row)) for row in rows]
        return {"sessions": sessions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

@app.post("/api/sessions/{session_id}/resume")
async def upload_resume(session_id: str, resume: UploadFile = File(...)):
    """Upload resume for a session"""
    try:
        # Read resume content
        content = await resume.read()
        resume_text = content.decode('utf-8') if resume.content_type == 'text/plain' else str(content)
        
        # Update session with resume
        conn = sqlite3.connect("interview_sessions.db")
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE sessions SET resume_content = ? WHERE id = ?",
            (resume_text, session_id)
        )
        
        conn.commit()
        conn.close()
        
        return {"message": "Resume uploaded successfully", "filename": resume.filename}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload resume: {str(e)}")

@app.post("/api/sessions/{session_id}/complete")
async def complete_session(session_id: str, evaluation_data: dict):
    """Complete an interview session with evaluation"""
    try:
        conn = sqlite3.connect("interview_sessions.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE sessions 
            SET status = 'completed', interview_data = ?
            WHERE id = ?
        """, (json.dumps(evaluation_data), session_id))
        
        conn.commit()
        conn.close()
        
        return {"message": "Session completed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete session: {str(e)}")

# WebSocket endpoint for real-time communication
active_connections: Dict[str, WebSocket] = {}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    active_connections[session_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now - can be extended for real-time features
            await websocket.send_text(f"Echo: {data}")
            
    except WebSocketDisconnect:
        if session_id in active_connections:
            del active_connections[session_id]

# Static endpoints for demo data
@app.get("/api/demo/questions")
async def get_demo_questions():
    """Get demo interview questions"""
    questions = {
        "technical": [
            "What is your experience with Python?",
            "Explain the difference between list and tuple.",
            "How do you handle exceptions in your code?",
            "What is object-oriented programming?",
        ],
        "behavioral": [
            "Tell me about a challenging project you worked on.",
            "How do you handle tight deadlines?",
            "Describe a time when you had to work in a team.",
        ]
    }
    return questions

@app.get("/api/demo/evaluation")
async def get_demo_evaluation():
    """Get demo evaluation criteria"""
    evaluation = {
        "criteria": [
            {"name": "Technical Skills", "weight": 0.4},
            {"name": "Communication", "weight": 0.3},
            {"name": "Problem Solving", "weight": 0.3}
        ],
        "scoring": {
            "excellent": {"min": 8.5, "max": 10},
            "good": {"min": 7.0, "max": 8.4},
            "satisfactory": {"min": 5.5, "max": 6.9},
            "needs_improvement": {"min": 0, "max": 5.4}
        }
    }
    return evaluation

@app.post("/api/sessions/{session_id}/join")
async def join_session(session_id: str, request_data: dict):
    """Join a session and get LiveKit access token"""
    try:
        # Get session from database
        conn = sqlite3.connect("interview_sessions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get session data
        columns = [description[0] for description in cursor.description]
        session_data = dict(zip(columns, row))
        room_name = session_data['room_name']
        participant_name = session_data['participant_name']
        
        # Generate new token for joining
        if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
            raise HTTPException(status_code=500, detail="LiveKit credentials not configured")
        
        participant_token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        participant_token.with_identity(f"participant-{session_id}")
        participant_token.with_name(participant_name)
        participant_grants = VideoGrants(room_join=True, room=room_name)
        participant_token.with_grants(participant_grants)
        
        return {
            "success": True,
            "access_token": participant_token.to_jwt(),
            "livekit_url": LIVEKIT_URL,
            "room_name": room_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to join session: {str(e)}")

@app.post("/api/sessions/{session_id}/start")
async def start_interview_session(session_id: str):
    """Start the interview for a session"""
    try:
        # Update session status to started
        conn = sqlite3.connect("interview_sessions.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sessions 
            SET status = 'started', interview_data = JSON_SET(COALESCE(interview_data, '{}'), '$.started_at', datetime('now'))
            WHERE id = ?
        """, (session_id,))
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Interview started successfully",
            "status": "started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting LiveKit Interview Backend...")
    print(f"🌐 API Server: http://localhost:8002")
    print(f"📊 Health Check: http://localhost:8002/health")
    print(f"📚 API Docs: http://localhost:8002/docs")
    print("=" * 50)
    
    uvicorn.run(
        "simple_backend:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
