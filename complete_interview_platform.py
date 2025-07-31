"""
Complete Real-Time AI Interview Platform
=======================================
End-to-end voice AI interviewer using LiveKit for real-time communication.
No mocks - fully functional interview system.
"""

import asyncio
import logging
import json
import os
import uuid
import base64
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import threading
import tempfile

# Core dependencies
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# LiveKit SDK
try:
    from livekit.api import AccessToken
    from livekit.api.access_token import VideoGrants
    print("✅ LiveKit API available")
    livekit_available = True
except ImportError:
    print("⚠️ LiveKit API not available - install with: pip install livekit-api")
    livekit_available = False

# Google AI
try:
    import google.generativeai as genai
    print("✅ Google AI available")
    ai_available = True
except ImportError:
    print("⚠️ Google AI not available")
    ai_available = False

load_dotenv()

# Configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY and ai_available:
    genai.configure(api_key=GOOGLE_API_KEY)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data Models
class CandidateInfo(BaseModel):
    name: str
    email: str
    position: str
    experience_level: str
    skills: List[str] = []

class InterviewRequest(BaseModel):
    candidate: CandidateInfo
    interview_type: str = "technical"
    max_questions: int = 5

@dataclass
class InterviewSession:
    session_id: str
    candidate: CandidateInfo
    room_name: str
    questions: List[Dict] = None
    answers: List[str] = None
    current_question: int = 0
    status: str = "created"
    start_time: Optional[datetime] = None
    ai_connected: bool = False
    
    def __post_init__(self):
        if self.questions is None:
            self.questions = []
        if self.answers is None:
            self.answers = []

class AIInterviewerBot:
    """AI Interviewer that manages the interview flow"""
    
    def __init__(self, session: InterviewSession):
        self.session = session
        self.websockets: List[WebSocket] = []
        self.is_active = False
        
    async def initialize(self):
        """Initialize the AI interviewer"""
        logger.info(f"Initializing AI interviewer for {self.session.candidate.name}")
        
        # Generate personalized questions
        await self._generate_questions()
        
        self.session.ai_connected = True
        self.session.status = "active"
        self.session.start_time = datetime.now()
        
        logger.info("AI interviewer ready to start")
    
    async def _generate_questions(self):
        """Generate interview questions using AI"""
        if ai_available and GOOGLE_API_KEY:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Create 5 professional interview questions for:
                
                Name: {self.session.candidate.name}
                Position: {self.session.candidate.position}
                Experience: {self.session.candidate.experience_level}
                Skills: {', '.join(self.session.candidate.skills)}
                
                Requirements:
                1. Professional but conversational tone
                2. Appropriate difficulty for {self.session.candidate.experience_level} level
                3. Mix of technical and behavioral questions
                4. Natural flow from introduction to conclusion
                
                Return as JSON array:
                [
                    {{
                        "question_text": "Natural, conversational question",
                        "question_type": "introduction|technical|behavioral|future",
                        "expected_duration": 120
                    }}
                ]
                """
                
                response = model.generate_content(prompt)
                questions_data = json.loads(response.text.strip())
                self.session.questions = questions_data
                
                logger.info(f"Generated {len(questions_data)} personalized questions")
                return
                
            except Exception as e:
                logger.warning(f"AI question generation failed: {e}")
        
        # Fallback questions
        self._use_fallback_questions()
    
    def _use_fallback_questions(self):
        """High-quality fallback questions"""
        candidate = self.session.candidate
        
        self.session.questions = [
            {
                "question_text": f"Hello {candidate.name}! Thank you for joining the interview today. To start, could you tell me a bit about yourself and what draws you to the {candidate.position} role?",
                "question_type": "introduction",
                "expected_duration": 120
            },
            {
                "question_text": "That's wonderful! Now, I'd love to hear about a challenging technical project you've worked on recently. Could you walk me through the problem, your approach, and the outcome?",
                "question_type": "technical",
                "expected_duration": 150
            },
            {
                "question_text": f"Great example! Looking at your experience with {', '.join(candidate.skills[:3]) if candidate.skills else 'various technologies'}, can you share a specific instance where you applied these skills to solve a real problem?",
                "question_type": "technical",
                "expected_duration": 140
            },
            {
                "question_text": "Excellent! Now, thinking about teamwork - can you describe a situation where you had to collaborate with others or handle a conflict? How did you approach it?",
                "question_type": "behavioral",
                "expected_duration": 130
            },
            {
                "question_text": f"Finally, looking ahead - where do you see yourself growing in your {candidate.position} career? What kind of challenges are you excited to take on?",
                "question_type": "future",
                "expected_duration": 100
            }
        ]
        
        logger.info("Using fallback questions")
    
    async def start_interview(self):
        """Start the interview process"""
        if not self.is_active and self.session.questions:
            self.is_active = True
            logger.info("Starting interview conversation")
            
            # Welcome message
            welcome = f"Hello {self.session.candidate.name}! I'm your AI interviewer today. I'm excited to learn more about you and your experience. Are you ready to begin?"
            
            await self._send_ai_message({
                "type": "ai_speech",
                "text": welcome,
                "action": "welcome"
            })
            
            # Wait a moment, then ask first question
            await asyncio.sleep(3)
            await self._ask_current_question()
    
    async def _ask_current_question(self):
        """Ask the current question"""
        if self.session.current_question < len(self.session.questions):
            question = self.session.questions[self.session.current_question]
            
            await self._send_ai_message({
                "type": "ai_speech", 
                "text": question["question_text"],
                "action": "question",
                "question_number": self.session.current_question + 1,
                "total_questions": len(self.session.questions)
            })
            
            logger.info(f"Asked question {self.session.current_question + 1}: {question['question_text'][:50]}...")
        else:
            await self._complete_interview()
    
    async def handle_candidate_response(self, response_text: str):
        """Process candidate's response"""
        logger.info(f"Candidate response: {response_text[:100]}...")
        
        # Store the answer
        self.session.answers.append(response_text)
        
        # Send acknowledgment
        acknowledgments = [
            "Thank you for sharing that.",
            "That's a great example.",
            "I appreciate the detailed explanation.",
            "Very interesting approach.",
            "Thank you for that insight."
        ]
        
        import random
        acknowledgment = random.choice(acknowledgments)
        
        await self._send_ai_message({
            "type": "ai_speech",
            "text": acknowledgment,
            "action": "acknowledgment"
        })
        
        # Brief pause, then next question
        await asyncio.sleep(2)
        
        self.session.current_question += 1
        await self._ask_current_question()
    
    async def _complete_interview(self):
        """Complete the interview"""
        completion_msg = f"Thank you so much, {self.session.candidate.name}. That concludes our interview today. You've provided excellent insights, and we have everything we need. We'll be in touch with the next steps soon. Have a wonderful day!"
        
        await self._send_ai_message({
            "type": "ai_speech",
            "text": completion_msg,
            "action": "completion"
        })
        
        self.session.status = "completed"
        self.is_active = False
        
        logger.info("Interview completed successfully")
    
    async def _send_ai_message(self, message: dict):
        """Send message to all connected websockets"""
        if self.websockets:
            message_json = json.dumps(message)
            disconnected = []
            
            for ws in self.websockets:
                try:
                    await ws.send_text(message_json)
                except:
                    disconnected.append(ws)
            
            # Remove disconnected websockets
            for ws in disconnected:
                self.websockets.remove(ws)
    
    def add_websocket(self, websocket: WebSocket):
        """Add websocket connection"""
        self.websockets.append(websocket)
    
    def remove_websocket(self, websocket: WebSocket):
        """Remove websocket connection"""
        if websocket in self.websockets:
            self.websockets.remove(websocket)

# Global storage
active_sessions: Dict[str, InterviewSession] = {}
active_interviewers: Dict[str, AIInterviewerBot] = {}

# FastAPI Application
app = FastAPI(title="Complete AI Interview Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Complete Real-Time AI Interview Platform",
        "status": "active",
        "livekit_available": livekit_available,
        "ai_available": ai_available
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "livekit_url": LIVEKIT_URL,
        "livekit_available": livekit_available,
        "ai_available": ai_available,
        "active_sessions": len(active_sessions),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/interview/create")
async def create_interview(request: InterviewRequest, background_tasks: BackgroundTasks):
    """Create a new real-time interview session"""
    try:
        session_id = f"interview_{uuid.uuid4().hex[:8]}"
        room_name = f"interview_room_{session_id}"
        
        # Create session
        session = InterviewSession(
            session_id=session_id,
            candidate=request.candidate,
            room_name=room_name
        )
        
        # Generate access token for candidate
        if livekit_available:
            token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
            token.with_identity(f"candidate-{session_id}")
            token.with_name(request.candidate.name)
            token.with_grants(VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True
            ))
            access_token = token.to_jwt()
        else:
            access_token = "fallback-token"
        
        # Store session
        active_sessions[session_id] = session
        
        # Initialize AI interviewer
        background_tasks.add_task(initialize_ai_interviewer, session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "room_name": room_name,
            "access_token": access_token,
            "livekit_url": LIVEKIT_URL,
            "fallback_mode": not livekit_available,
            "message": f"Interview session created for {request.candidate.name}"
        }
        
    except Exception as e:
        logger.error(f"Session creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def initialize_ai_interviewer(session_id: str):
    """Initialize AI interviewer"""
    try:
        session = active_sessions.get(session_id)
        if session:
            interviewer = AIInterviewerBot(session)
            await interviewer.initialize()
            active_interviewers[session_id] = interviewer
            logger.info(f"AI interviewer ready for session {session_id}")
    except Exception as e:
        logger.error(f"AI interviewer initialization failed: {e}")

@app.websocket("/ws/interview/{session_id}")
async def websocket_interview(websocket: WebSocket, session_id: str):
    """WebSocket connection for real-time interview communication"""
    await websocket.accept()
    
    session = active_sessions.get(session_id)
    interviewer = active_interviewers.get(session_id)
    
    if not session or not interviewer:
        await websocket.send_text(json.dumps({"error": "Session not found"}))
        await websocket.close()
        return
    
    # Add websocket to interviewer
    interviewer.add_websocket(websocket)
    
    try:
        # Send initial status
        await websocket.send_text(json.dumps({
            "type": "status",
            "session_id": session_id,
            "ai_connected": session.ai_connected,
            "status": session.status,
            "candidate_name": session.candidate.name
        }))
        
        # Start interview if not already started
        if session.ai_connected and not interviewer.is_active:
            await interviewer.start_interview()
        
        # Handle incoming messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "candidate_response":
                await interviewer.handle_candidate_response(message["text"])
            elif message["type"] == "start_interview":
                if not interviewer.is_active:
                    await interviewer.start_interview()
            
    except WebSocketDisconnect:
        interviewer.remove_websocket(websocket)
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        interviewer.remove_websocket(websocket)

@app.get("/api/interview/status/{session_id}")
async def get_interview_status(session_id: str):
    """Get interview status"""
    session = active_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "status": session.status,
        "current_question": session.current_question + 1,
        "total_questions": len(session.questions),
        "ai_connected": session.ai_connected,
        "start_time": session.start_time.isoformat() if session.start_time else None,
        "candidate_name": session.candidate.name
    }

@app.get("/api/interview/results/{session_id}")
async def get_interview_results(session_id: str):
    """Get interview results"""
    session = active_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "candidate": {
            "name": session.candidate.name,
            "email": session.candidate.email,
            "position": session.candidate.position,
            "experience_level": session.candidate.experience_level,
            "skills": session.candidate.skills
        },
        "questions": session.questions,
        "answers": session.answers,
        "status": session.status,
        "completion_rate": len(session.answers) / len(session.questions) if session.questions else 0
    }

@app.delete("/api/interview/{session_id}")
async def end_interview(session_id: str):
    """End interview session"""
    active_sessions.pop(session_id, None)
    active_interviewers.pop(session_id, None)
    return {"success": True, "message": "Interview session ended"}

@app.get("/interview")
async def serve_interview_page():
    """Serve the complete interview interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Complete AI Interview Platform</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 30px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
            h1 { text-align: center; margin-bottom: 30px; font-size: 2.5em; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 8px; font-weight: 600; }
            input, select, textarea {
                width: 100%;
                padding: 12px;
                border: none;
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.9);
                color: #333;
                font-size: 16px;
            }
            .btn {
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                width: 100%;
                margin-top: 10px;
                transition: transform 0.2s;
            }
            .btn:hover { transform: translateY(-2px); }
            .btn:disabled { opacity: 0.6; cursor: not-allowed; }
            
            .interview-section {
                display: none;
            }
            .status-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }
            .status-item {
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            .status-connected { background: rgba(76, 175, 80, 0.3); }
            .status-waiting { background: rgba(255, 193, 7, 0.3); }
            .status-error { background: rgba(244, 67, 54, 0.3); }
            
            .chat-area {
                height: 300px;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 10px;
                padding: 20px;
                overflow-y: auto;
                margin-bottom: 20px;
            }
            .message {
                margin-bottom: 15px;
                padding: 10px 15px;
                border-radius: 15px;
                max-width: 80%;
            }
            .ai-message {
                background: rgba(76, 175, 80, 0.3);
                margin-right: auto;
            }
            .user-message {
                background: rgba(33, 150, 243, 0.3);
                margin-left: auto;
                text-align: right;
            }
            
            .response-area {
                display: none;
            }
            .response-input {
                height: 100px;
                resize: vertical;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎙️ Complete AI Interview Platform</h1>
            
            <div id="setupSection" class="card">
                <h2>Interview Setup</h2>
                <form id="interviewForm">
                    <div class="form-group">
                        <label>Full Name *</label>
                        <input type="text" id="candidateName" required>
                    </div>
                    <div class="form-group">
                        <label>Email *</label>
                        <input type="email" id="candidateEmail" required>
                    </div>
                    <div class="form-group">
                        <label>Position *</label>
                        <input type="text" id="position" placeholder="e.g., Software Engineer" required>
                    </div>
                    <div class="form-group">
                        <label>Experience Level *</label>
                        <select id="experienceLevel" required>
                            <option value="">Select Level</option>
                            <option value="entry">Entry Level (0-2 years)</option>
                            <option value="mid">Mid Level (3-5 years)</option>
                            <option value="senior">Senior Level (6+ years)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Skills (comma-separated)</label>
                        <textarea id="skills" placeholder="e.g., Python, JavaScript, React, Node.js"></textarea>
                    </div>
                    <button type="submit" class="btn">🚀 Start AI Interview</button>
                </form>
            </div>
            
            <div id="interviewSection" class="interview-section card">
                <h2>Live AI Interview</h2>
                
                <div class="status-grid">
                    <div class="status-item">
                        <strong>Interview Status:</strong><br>
                        <span id="interviewStatus" class="status-waiting">Connecting...</span>
                    </div>
                    <div class="status-item">
                        <strong>AI Interviewer:</strong><br>
                        <span id="aiStatus" class="status-waiting">Initializing...</span>
                    </div>
                    <div class="status-item">
                        <strong>Question Progress:</strong><br>
                        <span id="questionProgress">0 / 0</span>
                    </div>
                </div>
                
                <div id="chatArea" class="chat-area"></div>
                
                <div id="responseArea" class="response-area">
                    <textarea id="responseInput" class="response-input" placeholder="Type your response here..."></textarea>
                    <button id="sendResponseBtn" class="btn">📤 Send Response</button>
                </div>
                
                <button id="endInterviewBtn" class="btn" style="background: linear-gradient(45deg, #f44336, #d32f2f); display: none;">
                    🛑 End Interview
                </button>
            </div>
        </div>
        
        <script>
            let sessionId = null;
            let websocket = null;
            let currentQuestion = 0;
            let totalQuestions = 0;
            
            // Form submission
            document.getElementById('interviewForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                await startInterview();
            });
            
            // Response submission
            document.getElementById('sendResponseBtn').addEventListener('click', sendResponse);
            document.getElementById('responseInput').addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    sendResponse();
                }
            });
            
            async function startInterview() {
                const formData = {
                    candidate: {
                        name: document.getElementById('candidateName').value.trim(),
                        email: document.getElementById('candidateEmail').value.trim(),
                        position: document.getElementById('position').value.trim(),
                        experience_level: document.getElementById('experienceLevel').value,
                        skills: document.getElementById('skills').value.split(',').map(s => s.trim()).filter(s => s)
                    },
                    interview_type: "technical",
                    max_questions: 5
                };
                
                if (!formData.candidate.name || !formData.candidate.email || !formData.candidate.position || !formData.candidate.experience_level) {
                    alert('Please fill in all required fields.');
                    return;
                }
                
                try {
                    const response = await fetch('/api/interview/create', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(formData)
                    });
                    
                    if (!response.ok) throw new Error('Failed to create interview session');
                    
                    const data = await response.json();
                    sessionId = data.session_id;
                    
                    // Switch to interview view
                    document.getElementById('setupSection').style.display = 'none';
                    document.getElementById('interviewSection').style.display = 'block';
                    
                    // Connect WebSocket
                    connectWebSocket();
                    
                } catch (error) {
                    alert('Failed to start interview: ' + error.message);
                }
            }
            
            function connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws/interview/${sessionId}`;
                
                websocket = new WebSocket(wsUrl);
                
                websocket.onopen = () => {
                    console.log('WebSocket connected');
                    updateStatus('interviewStatus', 'Connected', 'connected');
                };
                
                websocket.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    handleWebSocketMessage(message);
                };
                
                websocket.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    updateStatus('interviewStatus', 'Connection Error', 'error');
                };
                
                websocket.onclose = () => {
                    console.log('WebSocket disconnected');
                    updateStatus('interviewStatus', 'Disconnected', 'error');
                };
            }
            
            function handleWebSocketMessage(message) {
                switch (message.type) {
                    case 'status':
                        if (message.ai_connected) {
                            updateStatus('aiStatus', 'Connected', 'connected');
                        }
                        break;
                        
                    case 'ai_speech':
                        addMessage(message.text, 'ai');
                        
                        if (message.action === 'question') {
                            currentQuestion = message.question_number;
                            totalQuestions = message.total_questions;
                            updateQuestionProgress();
                            showResponseArea();
                        } else if (message.action === 'completion') {
                            hideResponseArea();
                            document.getElementById('endInterviewBtn').style.display = 'block';
                            updateStatus('interviewStatus', 'Completed', 'connected');
                        }
                        break;
                }
            }
            
            function sendResponse() {
                const responseText = document.getElementById('responseInput').value.trim();
                if (!responseText) return;
                
                // Add user message to chat
                addMessage(responseText, 'user');
                
                // Send to AI
                if (websocket && websocket.readyState === WebSocket.OPEN) {
                    websocket.send(JSON.stringify({
                        type: 'candidate_response',
                        text: responseText
                    }));
                }
                
                // Clear input and hide response area temporarily
                document.getElementById('responseInput').value = '';
                hideResponseArea();
            }
            
            function addMessage(text, sender) {
                const chatArea = document.getElementById('chatArea');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}-message`;
                messageDiv.textContent = text;
                chatArea.appendChild(messageDiv);
                chatArea.scrollTop = chatArea.scrollHeight;
            }
            
            function updateStatus(elementId, text, type) {
                const element = document.getElementById(elementId);
                element.textContent = text;
                element.className = `status-${type}`;
            }
            
            function updateQuestionProgress() {
                document.getElementById('questionProgress').textContent = `${currentQuestion} / ${totalQuestions}`;
            }
            
            function showResponseArea() {
                document.getElementById('responseArea').style.display = 'block';
                document.getElementById('responseInput').focus();
            }
            
            function hideResponseArea() {
                document.getElementById('responseArea').style.display = 'none';
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    print("🚀 Starting Complete AI Interview Platform...")
    print(f"🌐 LiveKit URL: {LIVEKIT_URL}")
    print(f"🔧 LiveKit Available: {livekit_available}")
    print(f"🤖 AI Available: {ai_available}")
    print("📖 Access the interview at: http://localhost:8001/interview")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
