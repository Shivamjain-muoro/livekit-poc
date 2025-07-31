"""
Real-Time Voice AI Interview Agent
================================
Fully automated voice-driven interview system using LiveKit, STT, TTS, and LLM.
No manual buttons - natural conversation flow like human interviews.
"""

import os
import asyncio
import json
import uuid
import logging
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# LiveKit imports
from livekit import api, rtc
from livekit.api import AccessToken, VideoGrants, RoomServiceClient, CreateRoomRequest
from livekit.rtc import Room, TrackSubscription, AudioFrame

# AI/ML imports
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import pygame
import io

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize AI
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
    ai_available = True
    print("✅ Google Gemini AI initialized for real-time evaluation")
else:
    ai_model = None
    ai_available = False
    print("⚠️ No Google API key - using fallback responses")

# Initialize speech recognition
recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 1.0  # Seconds of silence to end phrase

# Initialize TTS system
pygame.mixer.init()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data Models
class Candidate(BaseModel):
    name: str
    email: str
    position: str
    experience_level: str
    skills: List[str] = []

class VoiceInterviewRequest(BaseModel):
    candidate: Candidate
    interview_type: str = "technical"
    max_questions: int = 5
    enable_real_time_feedback: bool = True

class VoiceSessionResponse(BaseModel):
    success: bool
    session_id: str
    room_name: str
    access_token: str
    livekit_url: str
    ai_agent_ready: bool
    message: str

class InterviewState(BaseModel):
    session_id: str
    candidate: Candidate
    room_name: str
    current_question_index: int = 0
    questions: List[Dict] = []
    answers: List[Dict] = []
    scores: List[int] = []
    feedback: List[str] = []
    status: str = "created"  # created, active, listening, evaluating, completed
    ai_agent_connected: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

# Global state
interview_sessions: Dict[str, InterviewState] = {}
active_ai_agents: Dict[str, 'AIInterviewAgent'] = {}

class AIInterviewAgent:
    """
    Real-time AI Interview Agent that handles the complete voice conversation.
    Automatically listens, evaluates, and responds without manual intervention.
    """
    
    def __init__(self, session_id: str, room_name: str):
        self.session_id = session_id
        self.room_name = room_name
        self.room: Optional[Room] = None
        self.is_connected = False
        self.is_listening = False
        self.audio_buffer = []
        self.conversation_active = True
        
    async def initialize(self):
        """Initialize the AI agent and connect to LiveKit room"""
        try:
            # Generate agent token
            token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
            token.with_identity(f"ai-agent-{self.session_id}")
            token.with_name("AI Interviewer")
            token.with_grants(VideoGrants(
                room_join=True,
                room=self.room_name,
                can_publish=True,
                can_subscribe=True,
                room_admin=True
            ))
            
            # Connect to room
            self.room = Room()
            
            # Set up event handlers
            self.room.on("track_subscribed", self._on_track_subscribed)
            self.room.on("participant_connected", self._on_participant_connected)
            self.room.on("participant_disconnected", self._on_participant_disconnected)
            
            # Connect to LiveKit
            await self.room.connect(LIVEKIT_URL, token.to_jwt())
            self.is_connected = True
            
            logger.info(f"AI Agent connected to room: {self.room_name}")
            
            # Update session state
            if self.session_id in interview_sessions:
                interview_sessions[self.session_id].ai_agent_connected = True
                interview_sessions[self.session_id].status = "active"
            
            # Start the interview after a brief delay
            await asyncio.sleep(2)
            await self.start_interview()
            
        except Exception as e:
            logger.error(f"Failed to initialize AI agent: {e}")
            raise
    
    async def _on_participant_connected(self, participant):
        """Handle when candidate joins the room"""
        if "candidate" in participant.identity:
            logger.info(f"Candidate joined: {participant.identity}")
            # Brief welcome, then start interview
            await asyncio.sleep(1)
            await self.speak_welcome()
    
    async def _on_participant_disconnected(self, participant):
        """Handle when participant leaves"""
        if "candidate" in participant.identity:
            logger.info(f"Candidate left: {participant.identity}")
            self.conversation_active = False
    
    async def _on_track_subscribed(self, track: rtc.Track, publication, participant):
        """Handle incoming audio from candidate"""
        if track.kind == rtc.TrackKind.KIND_AUDIO and "candidate" in participant.identity:
            logger.info("Subscribed to candidate's audio track")
            
            # Start continuous listening
            asyncio.create_task(self.continuous_audio_processing(track))
    
    async def continuous_audio_processing(self, audio_track):
        """Continuously process audio from candidate for speech recognition"""
        logger.info("Starting continuous audio processing...")
        
        while self.conversation_active and self.is_connected:
            try:
                if self.is_listening:
                    # Get audio frames
                    audio_frame = await audio_track.read()
                    if audio_frame:
                        self.audio_buffer.append(audio_frame)
                        
                        # Process audio buffer every 2 seconds
                        if len(self.audio_buffer) >= 50:  # Adjust based on sample rate
                            await self.process_audio_buffer()
                
                await asyncio.sleep(0.1)  # Small delay to prevent tight loop
                
            except Exception as e:
                logger.error(f"Audio processing error: {e}")
                await asyncio.sleep(1)
    
    async def process_audio_buffer(self):
        """Process accumulated audio for speech recognition"""
        if not self.audio_buffer:
            return
        
        try:
            # Convert audio frames to recognizable format
            # This is a simplified version - in production, you'd need proper audio processing
            audio_data = self.convert_frames_to_audio(self.audio_buffer)
            
            # Clear buffer
            self.audio_buffer = []
            
            # Perform speech recognition
            transcript = await self.speech_to_text(audio_data)
            
            if transcript and len(transcript.strip()) > 5:  # Ignore very short utterances
                logger.info(f"Candidate said: {transcript}")
                
                # Stop listening temporarily while processing
                self.is_listening = False
                
                # Process the answer
                await self.process_candidate_answer(transcript)
        
        except Exception as e:
            logger.error(f"Audio buffer processing error: {e}")
    
    def convert_frames_to_audio(self, frames) -> bytes:
        """Convert LiveKit audio frames to audio data for STT"""
        # This is a placeholder - implement actual audio conversion
        # You'll need to handle the specific audio format from LiveKit
        return b''  # Simplified for now
    
    async def speech_to_text(self, audio_data: bytes) -> Optional[str]:
        """Convert audio to text using speech recognition"""
        try:
            # Using Google Speech Recognition API (you can use other services)
            with sr.AudioFile(io.BytesIO(audio_data)) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)
                return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            logger.error(f"STT service error: {e}")
            return None
        except Exception as e:
            logger.error(f"STT processing error: {e}")
            return None
    
    async def speak_welcome(self):
        """AI agent welcomes the candidate"""
        session = interview_sessions.get(self.session_id)
        if not session:
            return
        
        welcome_message = f"Hello {session.candidate.name}! Welcome to your {session.candidate.position} interview. I'm your AI interviewer, and we'll be having a natural conversation. Are you ready to begin?"
        
        await self.text_to_speech(welcome_message)
        
        # Start listening for response
        await asyncio.sleep(2)
        self.is_listening = True
    
    async def start_interview(self):
        """Start the actual interview with first question"""
        session = interview_sessions.get(self.session_id)
        if not session:
            return
        
        # Generate questions if not already done
        if not session.questions:
            session.questions = await self.generate_interview_questions(session.candidate)
        
        session.start_time = datetime.now()
        session.status = "active"
        
        # Ask first question
        await self.ask_next_question()
    
    async def generate_interview_questions(self, candidate: Candidate) -> List[Dict]:
        """Generate personalized interview questions using AI"""
        if not ai_available:
            return self.get_fallback_questions(candidate.position)
        
        try:
            prompt = f"""
            Generate 5 progressive interview questions for a {candidate.experience_level} {candidate.position} position.
            
            Candidate skills: {', '.join(candidate.skills)}
            
            Requirements:
            1. Start with a warm-up question
            2. Include 2-3 technical questions appropriate for their level
            3. Include 1-2 behavioral questions
            4. Questions should build on each other
            5. Maintain conversational tone suitable for voice interaction
            
            Return as JSON array with this format:
            [
                {{
                    "question_text": "Tell me about yourself and your experience with {candidate.position}",
                    "question_type": "introduction",
                    "skills_tested": ["communication", "experience"],
                    "expected_duration": 120
                }}
            ]
            """
            
            response = ai_model.generate_content(prompt)
            questions_data = json.loads(response.text.strip())
            
            logger.info(f"Generated {len(questions_data)} AI questions for {candidate.name}")
            return questions_data
        
        except Exception as e:
            logger.error(f"Question generation error: {e}")
            return self.get_fallback_questions(candidate.position)
    
    def get_fallback_questions(self, position: str) -> List[Dict]:
        """Fallback questions when AI is unavailable"""
        base_questions = [
            {
                "question_text": f"Tell me about yourself and your experience in {position}",
                "question_type": "introduction",
                "skills_tested": ["communication", "experience"],
                "expected_duration": 120
            },
            {
                "question_text": "What interests you most about this role and our company?",
                "question_type": "motivation",
                "skills_tested": ["interest", "research"],
                "expected_duration": 90
            },
            {
                "question_text": "Describe a challenging project you worked on recently. What was your approach?",
                "question_type": "behavioral",
                "skills_tested": ["problem_solving", "technical_skills"],
                "expected_duration": 150
            },
            {
                "question_text": f"What technical skills do you think are most important for a {position}?",
                "question_type": "technical",
                "skills_tested": ["technical_knowledge", "industry_awareness"],
                "expected_duration": 120
            },
            {
                "question_text": "Where do you see yourself in the next 3-5 years?",
                "question_type": "future_goals",
                "skills_tested": ["career_planning", "ambition"],
                "expected_duration": 90
            }
        ]
        return base_questions
    
    async def ask_next_question(self):
        """Ask the next question in the interview"""
        session = interview_sessions.get(self.session_id)
        if not session or session.current_question_index >= len(session.questions):
            await self.complete_interview()
            return
        
        current_q = session.questions[session.current_question_index]
        question_text = current_q["question_text"]
        
        # Add some natural conversation flow
        if session.current_question_index == 0:
            intro = "Let's start with our first question. "
        else:
            intro = "Great! Now for the next question. "
        
        full_message = intro + question_text
        
        logger.info(f"Asking question {session.current_question_index + 1}: {question_text}")
        
        await self.text_to_speech(full_message)
        
        # Start listening for answer
        await asyncio.sleep(3)  # Give time for question to finish playing
        self.is_listening = True
    
    async def process_candidate_answer(self, transcript: str):
        """Process the candidate's answer using LLM evaluation"""
        session = interview_sessions.get(self.session_id)
        if not session:
            return
        
        try:
            current_question = session.questions[session.current_question_index]
            
            # Store the answer
            answer_data = {
                "question": current_question["question_text"],
                "answer": transcript,
                "timestamp": datetime.now().isoformat(),
                "duration": len(transcript.split()) * 0.5  # Rough estimate
            }
            session.answers.append(answer_data)
            
            # Evaluate answer using AI
            evaluation = await self.evaluate_answer(current_question, transcript, session.candidate)
            
            # Store evaluation
            session.scores.append(evaluation["score"])
            session.feedback.append(evaluation["feedback"])
            
            # Provide immediate feedback
            feedback_message = evaluation["spoken_feedback"]
            await self.text_to_speech(feedback_message)
            
            # Move to next question
            session.current_question_index += 1
            
            # Brief pause before next question
            await asyncio.sleep(2)
            await self.ask_next_question()
        
        except Exception as e:
            logger.error(f"Answer processing error: {e}")
            # Continue with next question on error
            session.current_question_index += 1
            await self.ask_next_question()
    
    async def evaluate_answer(self, question: Dict, answer: str, candidate: Candidate) -> Dict:
        """Evaluate candidate answer using LLM"""
        if not ai_available:
            return {
                "score": 7,  # Default neutral score
                "feedback": "Thank you for your response.",
                "spoken_feedback": "Thank you for that answer."
            }
        
        try:
            evaluation_prompt = f"""
            Evaluate this interview answer:
            
            Question: {question['question_text']}
            Question Type: {question['question_type']}
            Skills Tested: {question.get('skills_tested', [])}
            
            Candidate Answer: {answer}
            
            Candidate Profile:
            - Position: {candidate.position}
            - Experience: {candidate.experience_level}
            - Skills: {candidate.skills}
            
            Provide evaluation as JSON:
            {{
                "score": <1-10 rating>,
                "feedback": "<detailed written feedback>",
                "spoken_feedback": "<brief encouraging response for voice - keep under 20 words>",
                "strengths": ["<key strengths shown>"],
                "improvements": ["<areas to improve>"]
            }}
            
            Keep spoken_feedback brief and encouraging for natural conversation flow.
            """
            
            response = ai_model.generate_content(evaluation_prompt)
            evaluation = json.loads(response.text.strip())
            
            logger.info(f"Answer evaluated - Score: {evaluation['score']}/10")
            return evaluation
        
        except Exception as e:
            logger.error(f"Answer evaluation error: {e}")
            return {
                "score": 7,
                "feedback": "Thank you for your response.",
                "spoken_feedback": "Thank you for that answer."
            }
    
    async def complete_interview(self):
        """Complete the interview and provide final summary"""
        session = interview_sessions.get(self.session_id)
        if not session:
            return
        
        session.end_time = datetime.now()
        session.status = "completed"
        
        # Generate final summary
        summary = await self.generate_final_summary(session)
        
        # Speak final message
        final_message = f"Thank you {session.candidate.name}! That completes our interview. You did great! Your overall performance shows strong potential, and we'll be in touch soon with next steps."
        
        await self.text_to_speech(final_message)
        
        # Store final summary
        session.feedback.append(summary)
        
        logger.info(f"Interview completed for {session.candidate.name}")
        
        # Disconnect after brief delay
        await asyncio.sleep(5)
        await self.disconnect()
    
    async def generate_final_summary(self, session: InterviewState) -> str:
        """Generate comprehensive interview summary"""
        if not ai_available:
            avg_score = sum(session.scores) / len(session.scores) if session.scores else 7
            return f"Interview completed. Average score: {avg_score:.1f}/10"
        
        try:
            summary_prompt = f"""
            Generate a comprehensive interview summary:
            
            Candidate: {session.candidate.name}
            Position: {session.candidate.position}
            Experience Level: {session.candidate.experience_level}
            
            Questions and Answers:
            {json.dumps([{"q": q["question_text"], "a": a["answer"]} for q, a in zip(session.questions, session.answers)], indent=2)}
            
            Scores: {session.scores}
            Individual Feedback: {session.feedback[:-1]}  # Exclude this summary
            
            Provide comprehensive summary including:
            - Overall performance assessment
            - Key strengths demonstrated
            - Areas for improvement
            - Hiring recommendation
            - Overall score (1-10)
            """
            
            response = ai_model.generate_content(summary_prompt)
            return response.text.strip()
        
        except Exception as e:
            logger.error(f"Summary generation error: {e}")
            avg_score = sum(session.scores) / len(session.scores) if session.scores else 7
            return f"Interview completed. Average score: {avg_score:.1f}/10"
    
    async def text_to_speech(self, text: str):
        """Convert text to speech and play in LiveKit room"""
        try:
            # Generate speech using gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                tmp_path = tmp_file.name
            
            # Play audio in LiveKit room (simplified)
            # In production, you'd stream this audio to the LiveKit room
            logger.info(f"AI Speaking: {text[:50]}...")
            
            # For now, just log the speech
            # TODO: Implement actual audio streaming to LiveKit room
            
            # Cleanup
            os.unlink(tmp_path)
        
        except Exception as e:
            logger.error(f"TTS error: {e}")
    
    async def disconnect(self):
        """Disconnect AI agent from room"""
        try:
            if self.room and self.is_connected:
                await self.room.disconnect()
                self.is_connected = False
                logger.info(f"AI Agent disconnected from room: {self.room_name}")
        except Exception as e:
            logger.error(f"Disconnect error: {e}")

# FastAPI Application
app = FastAPI(title="Real-Time Voice AI Interview Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Real-Time Voice AI Interview Agent", "status": "active"}

@app.get("/voice-ai")
async def serve_voice_ai_interface():
    """Serve the voice AI interview interface"""
    try:
        with open("voice_ai_interview.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Voice AI interface not found")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "livekit_url": LIVEKIT_URL,
        "ai_enabled": ai_available,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/voice-interview/create", response_model=VoiceSessionResponse)
async def create_voice_interview(request: VoiceInterviewRequest):
    """Create a real-time voice interview session"""
    try:
        # Generate session
        session_id = f"voice_session_{uuid.uuid4().hex[:8]}"
        room_name = f"voice_interview_{session_id}"
        
        # Create LiveKit room
        room_service = RoomServiceClient(LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        room_request = CreateRoomRequest(name=room_name)
        await room_service.create_room(room_request)
        
        # Generate candidate access token
        token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        token.with_identity(f"candidate-{session_id}")
        token.with_name(request.candidate.name)
        token.with_grants(VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True
        ))
        
        # Create session state
        session = InterviewState(
            session_id=session_id,
            candidate=request.candidate,
            room_name=room_name,
            status="created"
        )
        interview_sessions[session_id] = session
        
        # Initialize AI agent
        ai_agent = AIInterviewAgent(session_id, room_name)
        active_ai_agents[session_id] = ai_agent
        
        # Start AI agent in background
        asyncio.create_task(ai_agent.initialize())
        
        return VoiceSessionResponse(
            success=True,
            session_id=session_id,
            room_name=room_name,
            access_token=token.to_jwt(),
            livekit_url=LIVEKIT_URL,
            ai_agent_ready=True,
            message=f"Voice interview session created for {request.candidate.name}. Join the room to start!"
        )
    
    except Exception as e:
        logger.error(f"Session creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.get("/api/voice-interview/status/{session_id}")
async def get_interview_status(session_id: str):
    """Get current interview status and progress"""
    session = interview_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "status": session.status,
        "current_question": session.current_question_index + 1,
        "total_questions": len(session.questions),
        "ai_agent_connected": session.ai_agent_connected,
        "start_time": session.start_time.isoformat() if session.start_time else None,
        "duration_minutes": (datetime.now() - session.start_time).total_seconds() / 60 if session.start_time else 0
    }

@app.get("/api/voice-interview/results/{session_id}")
async def get_interview_results(session_id: str):
    """Get complete interview results and analysis"""
    session = interview_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status != "completed":
        raise HTTPException(status_code=400, detail="Interview not completed yet")
    
    # Calculate metrics
    avg_score = sum(session.scores) / len(session.scores) if session.scores else 0
    duration = (session.end_time - session.start_time).total_seconds() / 60 if session.start_time and session.end_time else 0
    
    return {
        "session_id": session_id,
        "candidate": session.candidate.dict(),
        "interview_summary": {
            "total_questions": len(session.questions),
            "total_answers": len(session.answers),
            "average_score": round(avg_score, 1),
            "duration_minutes": round(duration, 1),
            "completion_rate": len(session.answers) / len(session.questions) if session.questions else 0
        },
        "detailed_results": [
            {
                "question": q["question_text"],
                "answer": a["answer"],
                "score": s,
                "feedback": f
            }
            for q, a, s, f in zip(session.questions, session.answers, session.scores, session.feedback[:-1])
        ],
        "final_summary": session.feedback[-1] if session.feedback else "No summary available",
        "timestamp": session.end_time.isoformat() if session.end_time else None
    }

@app.delete("/api/voice-interview/{session_id}")
async def end_interview(session_id: str):
    """Manually end an interview session"""
    session = interview_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Disconnect AI agent
    ai_agent = active_ai_agents.get(session_id)
    if ai_agent:
        await ai_agent.disconnect()
        del active_ai_agents[session_id]
    
    # Update session
    session.status = "terminated"
    session.end_time = datetime.now()
    
    return {"message": "Interview session ended", "session_id": session_id}

# WebSocket for real-time updates (optional)
@app.websocket("/ws/interview/{session_id}")
async def websocket_interview_updates(websocket: WebSocket, session_id: str):
    """WebSocket for real-time interview updates"""
    await websocket.accept()
    
    try:
        while True:
            session = interview_sessions.get(session_id)
            if session:
                update = {
                    "status": session.status,
                    "current_question": session.current_question_index + 1,
                    "total_questions": len(session.questions),
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_json(update)
            
            await asyncio.sleep(2)  # Update every 2 seconds
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")

if __name__ == "__main__":
    print("🚀 Starting Real-Time Voice AI Interview Agent...")
    print(f"🌐 API Server: http://localhost:8001")
    print(f"📊 Health Check: http://localhost:8001/health")
    print(f"📚 API Docs: http://localhost:8001/docs")
    print(f"🎙️ LiveKit URL: {LIVEKIT_URL}")
    print(f"🤖 AI Status: {'Enabled' if ai_available else 'Disabled (fallback mode)'}")
    print("=" * 60)
    
    uvicorn.run(
        "realtime_ai_interview_agent:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
