"""
Enhanced Real-Time Voice Interview Backend
=========================================
FastAPI backend optimized for real-time voice interviews with LiveKit integration.
Supports continuous interview flow, real-time evaluation, and voice-first interactions.
"""

import os
import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from livekit import AccessToken, VideoGrants, RoomServiceClient, CreateRoomRequest
from dotenv import load_dotenv

# Import our models and managers
from models.interview_models import *
from interview.manager import InterviewManager
from llm.evaluator import InterviewEvaluator, QuestionGenerator

load_dotenv()

# Configuration
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET") 
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://livekit-poc-q1ahw2wh.livekit.cloud")

# Global managers
interview_manager = InterviewManager()
evaluator = InterviewEvaluator()

# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
            except:
                self.disconnect(session_id)

manager = ConnectionManager()

# FastAPI app with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Real-Time Voice Interview Backend Starting...")
    print(f"🎙️ LiveKit URL: {LIVEKIT_URL}")
    print(f"🤖 LLM Integration: {'✅ Enabled' if evaluator.use_llm else '❌ Fallback Mode'}")
    yield
    print("🛑 Backend shutting down...")

app = FastAPI(
    title="Real-Time Voice Interview API",
    description="AI-powered voice interview system with LiveKit integration",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models for Voice Interview
class VoiceInterviewRequest(BaseModel):
    candidate: Candidate
    interview_type: str = "voice_technical"
    enable_real_time_feedback: bool = True
    voice_settings: Optional[Dict[str, Any]] = {}

class VoiceSessionResponse(BaseModel):
    success: bool
    session_id: str
    access_token: str
    livekit_url: str
    room_name: str
    agent_instructions: Dict[str, Any]
    message: str = ""

class RealTimeAnswerRequest(BaseModel):
    question_id: str
    answer_text: str
    duration: int
    confidence_score: Optional[float] = None
    audio_url: Optional[str] = None

class RealTimeAnswerResponse(BaseModel):
    success: bool
    feedback: Optional[Feedback] = None
    next_question: Optional[Question] = None
    is_complete: bool = False
    real_time_hints: Optional[List[str]] = []

class InterviewProgressUpdate(BaseModel):
    session_id: str
    current_question_index: int
    total_questions: int
    elapsed_time: int
    candidate_engagement_score: Optional[float] = None

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "livekit": "✅" if LIVEKIT_API_KEY and LIVEKIT_API_SECRET else "❌",
            "llm": "✅" if evaluator.use_llm else "❌",
            "database": "✅"
        }
    }

# Create voice interview session
@app.post("/api/voice-interview/create", response_model=VoiceSessionResponse)
async def create_voice_interview_session(request: VoiceInterviewRequest):
    """Create a new voice interview session with LiveKit room"""
    try:
        # Create interview session
        session = await interview_manager.create_session(
            request.candidate, 
            request.interview_type
        )
        
        if not session:
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        # Create LiveKit room
        room_service = RoomServiceClient(LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        room_request = CreateRoomRequest(name=session.room_name)
        await room_service.create_room(room_request)
        
        # Generate access token for candidate
        token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        token.with_identity(f"participant-{session.id}")
        token.with_name(request.candidate.name)
        token.with_grants(VideoGrants(room_join=True, room=session.room_name))
        
        # Agent instructions for the voice interview
        agent_instructions = {
            "interview_type": request.interview_type,
            "candidate_info": {
                "name": request.candidate.name,
                "position": request.candidate.position,
                "experience_level": request.candidate.experience_level
            },
            "total_questions": session.total_questions,
            "real_time_feedback": request.enable_real_time_feedback,
            "voice_settings": request.voice_settings or {
                "speech_rate": 1.0,
                "voice_type": "professional",
                "language": "en-US"
            }
        }
        
        return VoiceSessionResponse(
            success=True,
            session_id=session.id,
            access_token=token.to_jwt(),
            livekit_url=LIVEKIT_URL,
            room_name=session.room_name,
            agent_instructions=agent_instructions,
            message=f"Voice interview session created for {request.candidate.name}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create voice session: {str(e)}")

# Get session information
@app.get("/api/interview/session/{session_id}")
async def get_session_info(session_id: str):
    """Get detailed session information for the agent"""
    try:
        session = interview_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        questions = interview_manager.get_session_questions(session_id)
        
        return {
            "success": True,
            "session": {
                "id": session.id,
                "status": session.status,
                "current_question_index": session.current_question_index,
                "total_questions": session.total_questions,
                "start_time": session.start_time.isoformat() if session.start_time else None
            },
            "candidate": {
                "name": session.candidate.name,
                "email": session.candidate.email,
                "position": session.candidate.position,
                "experience_level": session.candidate.experience_level,
                "skills": session.candidate.skills
            },
            "questions": [
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "question_type": q.question_type,
                    "difficulty_level": q.difficulty_level,
                    "order_index": q.order_index,
                    "is_asked": q.is_asked
                } for q in questions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

# Start interview (returns first question)
@app.post("/api/interview/start/{session_id}")
async def start_voice_interview(session_id: str):
    """Start the voice interview and return the first question"""
    try:
        session = interview_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        first_question = interview_manager.start_interview(session_id)
        if not first_question:
            raise HTTPException(status_code=500, detail="Failed to start interview")
        
        questions = interview_manager.get_session_questions(session_id)
        estimated_duration = sum(q.expected_duration for q in questions) // 60
        
        # Notify via WebSocket
        await manager.send_message(session_id, {
            "type": "interview_started",
            "first_question": {
                "id": first_question.id,
                "question_text": first_question.question_text,
                "question_type": first_question.question_type,
                "difficulty_level": first_question.difficulty_level,
                "expected_duration": first_question.expected_duration
            },
            "total_questions": session.total_questions,
            "estimated_duration": estimated_duration
        })
        
        return {
            "success": True,
            "first_question": {
                "id": first_question.id,
                "question_text": first_question.question_text,
                "question_type": first_question.question_type,
                "difficulty_level": first_question.difficulty_level,
                "expected_duration": first_question.expected_duration,
                "order_index": first_question.order_index
            },
            "total_questions": session.total_questions,
            "estimated_duration": estimated_duration
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")

# Submit answer with real-time processing
@app.post("/api/interview/{session_id}/answer", response_model=RealTimeAnswerResponse)
async def submit_voice_answer(session_id: str, request: RealTimeAnswerRequest, background_tasks: BackgroundTasks):
    """Submit voice answer and get real-time feedback"""
    try:
        # Process answer asynchronously for faster response
        feedback, next_question, is_complete = await interview_manager.submit_answer(
            session_id=session_id,
            question_id=request.question_id,
            answer_text=request.answer_text,
            duration=request.duration
        )
        
        # Generate real-time hints if enabled
        real_time_hints = []
        if feedback.score < 3:  # If score is low, provide hints
            real_time_hints = [
                "Consider providing more specific examples",
                "Try to elaborate on your thought process",
                "Think about relevant experience you might have"
            ]
        
        # Notify via WebSocket about progress
        background_tasks.add_task(
            manager.send_message,
            session_id,
            {
                "type": "answer_processed",
                "feedback_score": feedback.score,
                "is_complete": is_complete,
                "current_question": request.question_id,
                "next_question_id": next_question.id if next_question else None
            }
        )
        
        return RealTimeAnswerResponse(
            success=True,
            feedback=feedback,
            next_question=next_question,
            is_complete=is_complete,
            real_time_hints=real_time_hints
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process answer: {str(e)}")

# Real-time interview progress tracking
@app.websocket("/ws/interview/{session_id}")
async def websocket_interview_progress(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time interview progress updates"""
    await manager.connect(websocket, session_id)
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message.get("type") == "progress_update":
                # Handle progress updates from the frontend/agent
                progress = InterviewProgressUpdate(**message.get("data", {}))
                await manager.send_message(session_id, {
                    "type": "progress_acknowledged",
                    "data": progress.dict()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)

# Get interview summary
@app.get("/api/interview/summary/{session_id}")
async def get_voice_interview_summary(session_id: str):
    """Get comprehensive interview summary with voice-specific metrics"""
    try:
        summary = interview_manager.generate_interview_summary(session_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Summary not found")
        
        # Add voice-specific metrics
        voice_metrics = {
            "total_speaking_time": summary.total_duration,
            "average_response_time": summary.total_duration // summary.questions_asked if summary.questions_asked > 0 else 0,
            "communication_clarity": "Good",  # This could be enhanced with actual analysis
            "engagement_level": "High" if summary.overall_score >= 4 else "Medium" if summary.overall_score >= 3 else "Low"
        }
        
        return {
            "success": True,
            "summary": summary.dict(),
            "voice_metrics": voice_metrics,
            "recommendations": {
                "overall": summary.recommendation,
                "technical_skills": "Strong" if summary.category_scores.get("technical", 0) >= 4 else "Needs improvement",
                "communication": "Excellent" if summary.overall_score >= 4 else "Good"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

# Voice interview demo page
@app.get("/voice-demo")
async def voice_interview_demo():
    """Serve the voice interview demo page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Voice Interview Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; }
            .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
            .success { background: #d4edda; color: #155724; }
            .info { background: #d1ecf1; color: #0c5460; }
            .warning { background: #fff3cd; color: #856404; }
            button { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; }
            .primary { background: #007bff; color: white; }
            .success-btn { background: #28a745; color: white; }
            input, select { padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }
            #videoContainer { width: 100%; height: 400px; background: #000; border-radius: 10px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>🎙️ Voice Interview Demo</h1>
        
        <div class="container">
            <h3>Candidate Information</h3>
            <input type="text" id="candidateName" placeholder="Full Name" value="John Doe">
            <input type="email" id="candidateEmail" placeholder="Email" value="john.doe@example.com">
            <input type="text" id="position" placeholder="Position" value="Software Engineer">
            <select id="experienceLevel">
                <option value="entry">Entry Level</option>
                <option value="mid" selected>Mid Level</option>
                <option value="senior">Senior Level</option>
                <option value="lead">Lead/Principal</option>
            </select>
            <br>
            <button class="primary" onclick="createVoiceSession()">🚀 Start Voice Interview</button>
        </div>
        
        <div class="container">
            <h3>Interview Status</h3>
            <div id="status" class="status info">Ready to start interview</div>
            <div id="videoContainer">
                <!-- LiveKit video will be inserted here -->
            </div>
            <button class="success-btn" onclick="joinRoom()" id="joinBtn" disabled>🎥 Join Interview Room</button>
        </div>
        
        <div class="container">
            <h3>Interview Progress</h3>
            <div id="progress">
                <p>Current Question: <span id="currentQuestion">Not started</span></p>
                <p>Progress: <span id="questionProgress">0/0</span></p>
                <p>Elapsed Time: <span id="elapsedTime">00:00</span></p>
            </div>
        </div>
        
        <script src="https://unpkg.com/livekit-client@2.5.7/dist/livekit-client.umd.js"></script>
        <script>
            let sessionData = null;
            let room = null;
            let startTime = null;
            
            async function createVoiceSession() {
                const candidate = {
                    name: document.getElementById('candidateName').value,
                    email: document.getElementById('candidateEmail').value,
                    position: document.getElementById('position').value,
                    experience_level: document.getElementById('experienceLevel').value,
                    skills: ['JavaScript', 'Python', 'Problem Solving']
                };
                
                try {
                    const response = await fetch('/api/voice-interview/create', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            candidate: candidate,
                            interview_type: 'voice_technical',
                            enable_real_time_feedback: true
                        })
                    });
                    
                    sessionData = await response.json();
                    
                    if (sessionData.success) {
                        document.getElementById('status').innerHTML = 
                            `✅ Session created! Room: ${sessionData.room_name}`;
                        document.getElementById('status').className = 'status success';
                        document.getElementById('joinBtn').disabled = false;
                    } else {
                        throw new Error('Failed to create session');
                    }
                } catch (error) {
                    document.getElementById('status').innerHTML = `❌ Error: ${error.message}`;
                    document.getElementById('status').className = 'status warning';
                }
            }
            
            async function joinRoom() {
                if (!sessionData) return;
                
                try {
                    room = new LiveKitClient.Room();
                    
                    room.on('participantConnected', (participant) => {
                        console.log('Participant connected:', participant.identity);
                    });
                    
                    room.on('trackSubscribed', (track, publication, participant) => {
                        if (track.kind === 'video') {
                            const videoElement = document.createElement('video');
                            videoElement.srcObject = new MediaStream([track.mediaStreamTrack]);
                            videoElement.autoplay = true;
                            videoElement.style.width = '100%';
                            videoElement.style.height = '100%';
                            document.getElementById('videoContainer').appendChild(videoElement);
                        }
                    });
                    
                    await room.connect(sessionData.livekit_url, sessionData.access_token);
                    
                    // Enable camera and microphone
                    await room.localParticipant.enableCameraAndMicrophone();
                    
                    document.getElementById('status').innerHTML = 
                        '🎥 Connected! The AI interviewer will start shortly...';
                    document.getElementById('status').className = 'status success';
                    
                    startTime = Date.now();
                    startTimer();
                    
                } catch (error) {
                    document.getElementById('status').innerHTML = `❌ Connection error: ${error.message}`;
                    document.getElementById('status').className = 'status warning';
                }
            }
            
            function startTimer() {
                setInterval(() => {
                    if (startTime) {
                        const elapsed = Math.floor((Date.now() - startTime) / 1000);
                        const minutes = Math.floor(elapsed / 60);
                        const seconds = elapsed % 60;
                        document.getElementById('elapsedTime').textContent = 
                            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                    }
                }, 1000);
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "realtime_voice_backend:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )
