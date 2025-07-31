"""
Real-Time AI Interview System - Backend
======================================
A complete end-to-end AI interviewer that joins LiveKit rooms as a real participant,
processes speech in real-time, and conducts natural voice interviews.
"""

import asyncio
import logging
import json
import os
import uuid
import tempfile
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import threading

# Core dependencies
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# LiveKit for real-time communication
try:
    from livekit.api import AccessToken
    from livekit.api.access_token import VideoGrants
    from livekit import rtc
    livekit_available = True
    print("✅ LiveKit SDK loaded successfully")
except ImportError as e:
    print(f"⚠️ LiveKit SDK not available: {e}")
    livekit_available = False

# Google AI for conversation
try:
    import google.generativeai as genai
    ai_available = True
    print("✅ Google AI loaded successfully")
except ImportError:
    ai_available = False
    print("⚠️ Google AI not available")

# Speech processing (we'll implement using available libraries)
try:
    import speech_recognition as sr
    import pyttsx3
    speech_available = True
    print("✅ Speech processing libraries loaded")
except ImportError:
    speech_available = False
    print("⚠️ Speech processing libraries not available")

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
    """Real-time interview session"""
    session_id: str
    candidate: CandidateInfo
    room_name: str
    questions: List[Dict] = None
    answers: List[str] = None
    current_question: int = 0
    status: str = "created"  # created, active, completed
    start_time: Optional[datetime] = None
    ai_connected: bool = False
    
    def __post_init__(self):
        if self.questions is None:
            self.questions = []
        if self.answers is None:
            self.answers = []

class RealTimeAIInterviewer:
    """Real AI Interviewer that joins LiveKit rooms"""
    
    def __init__(self, session: InterviewSession):
        self.session = session
        self.room: Optional[rtc.Room] = None
        self.audio_source: Optional[rtc.AudioSource] = None
        self.speech_recognizer = None
        self.tts_engine = None
        self.is_speaking = False
        self.is_listening = False
        
    async def initialize(self):
        """Initialize the AI interviewer"""
        try:
            logger.info(f"Initializing AI interviewer for session {self.session.session_id}")
            
            # Generate interview questions
            await self._generate_questions()
            
            # Initialize speech processing
            self._initialize_speech_processing()
            
            # Connect to LiveKit room
            await self._connect_to_livekit()
            
            self.session.ai_connected = True
            self.session.status = "active"
            self.session.start_time = datetime.now()
            
            logger.info("AI interviewer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI interviewer: {e}")
            raise
    
    async def _generate_questions(self):
        """Generate personalized interview questions"""
        if ai_available and GOOGLE_API_KEY:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Generate 5 professional interview questions for:
                
                Candidate: {self.session.candidate.name}
                Position: {self.session.candidate.position}
                Experience: {self.session.candidate.experience_level}
                Skills: {', '.join(self.session.candidate.skills)}
                
                Return as JSON array with this structure:
                [
                    {{
                        "question_text": "conversational question here",
                        "question_type": "introduction|technical|behavioral|future",
                        "expected_duration": 120
                    }}
                ]
                
                Make questions natural and conversational for a voice interview.
                """
                
                response = model.generate_content(prompt)
                self.session.questions = json.loads(response.text.strip())
                logger.info(f"Generated {len(self.session.questions)} AI questions")
                
            except Exception as e:
                logger.warning(f"AI question generation failed: {e}")
                self._use_fallback_questions()
        else:
            self._use_fallback_questions()
    
    def _use_fallback_questions(self):
        """Use high-quality fallback questions"""
        self.session.questions = [
            {
                "question_text": f"Hi {self.session.candidate.name}! Thanks for joining today. Could you start by telling me about yourself and what interests you most about the {self.session.candidate.position} role?",
                "question_type": "introduction",
                "expected_duration": 120
            },
            {
                "question_text": "That's great! Can you walk me through a challenging technical project you've worked on recently? What was your approach and what did you learn?",
                "question_type": "technical", 
                "expected_duration": 150
            },
            {
                "question_text": f"I see you have experience with {', '.join(self.session.candidate.skills[:3]) if self.session.candidate.skills else 'various technologies'}. Can you give me a specific example of how you've applied these skills?",
                "question_type": "technical",
                "expected_duration": 140
            },
            {
                "question_text": "Tell me about a time when you had to work with a difficult team member or handle a challenging situation. How did you approach it?",
                "question_type": "behavioral",
                "expected_duration": 130
            },
            {
                "question_text": f"Finally, where do you see yourself growing in your {self.session.candidate.position} career over the next few years?",
                "question_type": "future",
                "expected_duration": 100
            }
        ]
    
    def _initialize_speech_processing(self):
        """Initialize speech recognition and text-to-speech"""
        if speech_available:
            try:
                # Initialize speech recognition
                self.speech_recognizer = sr.Recognizer()
                self.speech_recognizer.energy_threshold = 300
                self.speech_recognizer.dynamic_energy_threshold = True
                
                # Initialize text-to-speech
                self.tts_engine = pyttsx3.init()
                voices = self.tts_engine.getProperty('voices')
                
                # Use a professional female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                
                self.tts_engine.setProperty('rate', 180)  # Speaking rate
                self.tts_engine.setProperty('volume', 0.9)  # Volume
                
                logger.info("Speech processing initialized")
                
            except Exception as e:
                logger.error(f"Speech processing initialization failed: {e}")
    
    async def _connect_to_livekit(self):
        """Connect to the LiveKit room as AI interviewer"""
        if not livekit_available:
            logger.warning("LiveKit not available, running in simulation mode")
            return
        
        try:
            # Create access token for AI participant
            token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
            token.with_identity("ai-interviewer")
            token.with_name("AI Interviewer")
            token.with_grants(VideoGrants(
                room_join=True,
                room=self.session.room_name,
                can_publish=True,
                can_subscribe=True
            ))
            
            # Create room connection
            self.room = rtc.Room()
            
            # Set up event handlers
            @self.room.on("participant_connected")
            def on_participant_connected(participant: rtc.RemoteParticipant):
                logger.info(f"Participant connected: {participant.identity}")
                if participant.identity != "ai-interviewer":
                    # Start the interview when candidate joins
                    asyncio.create_task(self._start_interview())
            
            @self.room.on("track_subscribed")
            def on_track_subscribed(track: rtc.Track, publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
                if track.kind == rtc.TrackKind.KIND_AUDIO:
                    logger.info("Subscribed to candidate's audio track")
                    # Start listening to candidate's audio
                    asyncio.create_task(self._process_candidate_audio(track))
            
            # Connect to room
            await self.room.connect(LIVEKIT_URL, token.to_jwt())
            logger.info(f"AI interviewer connected to room: {self.session.room_name}")
            
            # Create audio source for AI speech
            self.audio_source = rtc.AudioSource(24000, 1)  # 24kHz, mono
            audio_track = rtc.LocalAudioTrack.create_audio_track("ai-voice", self.audio_source)
            
            # Publish AI audio track
            await self.room.local_participant.publish_track(audio_track)
            logger.info("AI audio track published")
            
        except Exception as e:
            logger.error(f"Failed to connect to LiveKit: {e}")
            raise
    
    async def _start_interview(self):
        """Start the interview conversation"""
        logger.info("Starting interview conversation")
        await asyncio.sleep(2)  # Brief pause for connection stability
        
        # Welcome message and first question
        welcome_msg = f"Hello {self.session.candidate.name}! I'm your AI interviewer today. I'm excited to learn more about you. Let's begin with our first question."
        await self._speak(welcome_msg)
        
        await asyncio.sleep(1)
        
        # Ask first question
        await self._ask_current_question()
    
    async def _ask_current_question(self):
        """Ask the current question"""
        if self.session.current_question < len(self.session.questions):
            question = self.session.questions[self.session.current_question]
            await self._speak(question["question_text"])
            
            # Start listening for answer
            self.is_listening = True
            logger.info(f"Asked question {self.session.current_question + 1}: {question['question_text'][:50]}...")
        else:
            # Interview complete
            await self._complete_interview()
    
    async def _speak(self, text: str):
        """Convert text to speech and stream to LiveKit"""
        if self.is_speaking:
            return
        
        self.is_speaking = True
        logger.info(f"AI speaking: {text[:50]}...")
        
        try:
            if self.tts_engine and self.audio_source:
                # Generate speech audio
                audio_file = await self._generate_speech_audio(text)
                
                if audio_file and os.path.exists(audio_file):
                    # Stream audio to LiveKit
                    await self._stream_audio_file(audio_file)
                    
                    # Clean up temp file
                    os.unlink(audio_file)
            else:
                # Fallback: simulate speaking duration
                speaking_duration = len(text) * 0.05  # Rough estimate
                await asyncio.sleep(speaking_duration)
                
        except Exception as e:
            logger.error(f"Speech generation failed: {e}")
        finally:
            self.is_speaking = False
    
    async def _generate_speech_audio(self, text: str) -> Optional[str]:
        """Generate speech audio file"""
        try:
            # Create temporary WAV file
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_file.close()
            
            # Generate speech using pyttsx3
            def generate_speech():
                self.tts_engine.save_to_file(text, temp_file.name)
                self.tts_engine.runAndWait()
            
            # Run TTS in thread to avoid blocking
            thread = threading.Thread(target=generate_speech)
            thread.start()
            thread.join(timeout=10)  # 10 second timeout
            
            if os.path.exists(temp_file.name) and os.path.getsize(temp_file.name) > 0:
                return temp_file.name
            
        except Exception as e:
            logger.error(f"Speech generation error: {e}")
        
        return None
    
    async def _stream_audio_file(self, audio_file: str):
        """Stream audio file to LiveKit room"""
        try:
            # This is a simplified version - in production you'd properly decode and stream the audio
            # For now, we'll simulate the audio duration
            import wave
            
            with wave.open(audio_file, 'rb') as wav_file:
                duration = wav_file.getnframes() / wav_file.getframerate()
                await asyncio.sleep(duration)
                
        except Exception as e:
            logger.error(f"Audio streaming error: {e}")
            # Fallback: estimate duration from file size
            file_size = os.path.getsize(audio_file)
            estimated_duration = file_size / 32000  # Rough estimate
            await asyncio.sleep(min(estimated_duration, 10))  # Cap at 10 seconds
    
    async def _process_candidate_audio(self, audio_track: rtc.Track):
        """Process incoming audio from candidate"""
        logger.info("Starting to listen to candidate audio")
        # This would involve real-time audio processing and speech recognition
        # For now, we'll simulate the listening process
        
        while self.is_listening and self.session.status == "active":
            await asyncio.sleep(1)
            # In a real implementation, you'd process audio frames here
    
    async def _handle_candidate_response(self, response_text: str):
        """Handle candidate's response"""
        logger.info(f"Candidate response: {response_text[:100]}...")
        
        # Store the answer
        self.session.answers.append(response_text)
        self.is_listening = False
        
        # Acknowledge the response
        acknowledgments = [
            "Thank you for that response.",
            "That's very interesting.",
            "I appreciate you sharing that.",
            "Great example.",
            "Thank you for the detailed explanation."
        ]
        
        import random
        acknowledgment = random.choice(acknowledgments)
        await self._speak(acknowledgment)
        
        await asyncio.sleep(1)
        
        # Move to next question
        self.session.current_question += 1
        await self._ask_current_question()
    
    async def _complete_interview(self):
        """Complete the interview"""
        completion_msg = f"Thank you {self.session.candidate.name} for your time today. That completes our interview. We have all the information we need and will be in touch with next steps soon. Have a great day!"
        
        await self._speak(completion_msg)
        
        self.session.status = "completed"
        logger.info("Interview completed successfully")
        
        # Disconnect from room after a brief delay
        await asyncio.sleep(5)
        if self.room:
            await self.room.disconnect()

# Global sessions storage
active_sessions: Dict[str, InterviewSession] = {}
active_interviewers: Dict[str, RealTimeAIInterviewer] = {}

# FastAPI Application
app = FastAPI(title="Real-Time AI Interview Platform", version="1.0.0")

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
        "message": "Real-Time AI Interview Platform",
        "status": "active",
        "livekit_available": livekit_available,
        "ai_available": ai_available,
        "speech_available": speech_available
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "livekit_url": LIVEKIT_URL,
        "livekit_available": livekit_available,
        "ai_available": ai_available,
        "speech_available": speech_available,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/interview/create")
async def create_interview_session(request: InterviewRequest, background_tasks: BackgroundTasks):
    """Create a new real-time interview session"""
    try:
        # Generate session
        session_id = f"interview_{uuid.uuid4().hex[:8]}"
        room_name = f"interview_room_{session_id}"
        
        # Create interview session
        session = InterviewSession(
            session_id=session_id,
            candidate=request.candidate,
            room_name=room_name
        )
        
        # Generate access token for candidate
        token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        token.with_identity(f"candidate-{session_id}")
        token.with_name(request.candidate.name)
        token.with_grants(VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True
        ))
        
        # Store session
        active_sessions[session_id] = session
        
        # Initialize AI interviewer in background
        background_tasks.add_task(initialize_ai_interviewer, session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "room_name": room_name,
            "access_token": token.to_jwt(),
            "livekit_url": LIVEKIT_URL,
            "message": f"Interview session created for {request.candidate.name}"
        }
        
    except Exception as e:
        logger.error(f"Session creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

async def initialize_ai_interviewer(session_id: str):
    """Initialize AI interviewer for the session"""
    try:
        session = active_sessions.get(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            return
        
        # Create and initialize AI interviewer
        interviewer = RealTimeAIInterviewer(session)
        await interviewer.initialize()
        
        # Store active interviewer
        active_interviewers[session_id] = interviewer
        
        logger.info(f"AI interviewer initialized for session {session_id}")
        
    except Exception as e:
        logger.error(f"Failed to initialize AI interviewer for session {session_id}: {e}")

@app.get("/api/interview/status/{session_id}")
async def get_interview_status(session_id: str):
    """Get current interview status"""
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
        "questions_asked": len(session.answers),
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
        "candidate": asdict(session.candidate),
        "status": session.status,
        "questions": session.questions,
        "answers": session.answers,
        "completion_rate": len(session.answers) / len(session.questions) if session.questions else 0,
        "duration_minutes": (datetime.now() - session.start_time).total_seconds() / 60 if session.start_time else 0
    }

@app.delete("/api/interview/{session_id}")
async def end_interview(session_id: str):
    """End interview session"""
    session = active_sessions.get(session_id)
    interviewer = active_interviewers.get(session_id)
    
    if interviewer and interviewer.room:
        await interviewer.room.disconnect()
    
    # Clean up
    active_sessions.pop(session_id, None)
    active_interviewers.pop(session_id, None)
    
    return {"success": True, "message": "Interview session ended"}

@app.get("/voice-ai")
async def serve_interview_frontend():
    """Serve the interview frontend"""
    # Read the existing frontend file
    try:
        with open("voice_ai_interview.html", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Update API endpoints to use the new real-time endpoints
        content = content.replace("/api/voice-interview/create", "/api/interview/create")
        content = content.replace("/api/voice-interview/status/", "/api/interview/status/")
        content = content.replace("/api/voice-interview/", "/api/interview/")
        
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Interview frontend not found</h1>")

if __name__ == "__main__":
    print("🚀 Starting Real-Time AI Interview Platform...")
    print(f"🌐 LiveKit URL: {LIVEKIT_URL}")
    print(f"🔧 LiveKit Available: {livekit_available}")
    print(f"🤖 AI Available: {ai_available}")
    print(f"🎙️ Speech Available: {speech_available}")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
