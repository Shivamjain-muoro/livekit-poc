"""
Real-Time Voice Interview Agent
==============================
Advanced LiveKit agent for conducting voice-based interviews with:
- Real-time speech-to-text (STT)
- Text-to-speech (TTS) responses
- LLM evaluation and conversation flow
- Continuous interview state management
"""

import asyncio
import logging
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Optional, List
from enum import Enum

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import (
    JobContext, JobRequest, JobProcess, 
    Agent, RoomInputOptions, function_tool, 
    RunContext, Session
)
from livekit.plugins import google, silero, cartesia
from livekit.rtc import (
    AudioSource, VideoSource, RtcConfiguration,
    ParticipantEvent, TrackEvent, Track, 
    RoomEvent, Room, Participant
)
import aiohttp

load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8002")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterviewState(Enum):
    WAITING = "waiting"
    INTRODUCTION = "introduction"
    QUESTIONING = "questioning"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    ERROR = "error"

class RealTimeVoiceAgent:
    """Real-time voice interview agent"""
    
    def __init__(self):
        self.session_id: Optional[str] = None
        self.current_question_id: Optional[str] = None
        self.state = InterviewState.WAITING
        self.candidate_info: Optional[Dict] = None
        self.current_question_index = 0
        self.total_questions = 0
        self.conversation_history: List[Dict] = []
        
        # Initialize TTS and STT
        self.tts = google.TTS(
            voice="en-US-Standard-H",  # Female voice
            language="en-US",
            speed=1.0
        ) if GOOGLE_API_KEY else silero.TTS(
            language="en",
            speaker="v3_en"
        )
        
        self.stt = google.STT(
            language="en-US",
            detect_language=True
        ) if GOOGLE_API_KEY else None
        
    async def on_participant_connected(self, participant: Participant):
        """Handle when a participant joins the room"""
        logger.info(f"Participant connected: {participant.identity}")
        
        if participant.identity.startswith("participant-"):
            # Extract session ID from participant identity
            self.session_id = participant.identity.replace("participant-", "")
            logger.info(f"Session ID: {self.session_id}")
            
            # Start interview flow
            await self.start_interview_flow()
    
    async def on_track_published(self, publication, participant: Participant):
        """Handle when audio track is published"""
        if publication.kind == "audio" and participant.identity.startswith("participant-"):
            # Subscribe to audio track for STT
            track = await publication.track.get()
            if track:
                await self.setup_speech_recognition(track)
    
    async def start_interview_flow(self):
        """Initialize and start the interview"""
        try:
            self.state = InterviewState.INTRODUCTION
            
            # Get session info from backend
            session_info = await self.get_session_info()
            if not session_info:
                await self.speak("I'm sorry, I couldn't find your interview session. Please contact support.")
                return
            
            self.candidate_info = session_info.get("candidate", {})
            self.total_questions = session_info.get("total_questions", 5)
            
            # Welcome message
            welcome_message = f"""
            Hello {self.candidate_info.get('name', 'there')}! Welcome to your interview for the {self.candidate_info.get('position', 'position')} role.
            
            I'm your AI interviewer today. We'll have a conversation with {self.total_questions} questions. 
            Please speak clearly, and take your time with your responses. 
            
            Are you ready to begin?
            """
            
            await self.speak(welcome_message)
            
            # Start listening for "ready" confirmation
            self.state = InterviewState.QUESTIONING
            await self.start_first_question()
            
        except Exception as e:
            logger.error(f"Error starting interview: {e}")
            self.state = InterviewState.ERROR
            await self.speak("I'm experiencing technical difficulties. Please try again later.")
    
    async def start_first_question(self):
        """Start the interview with the first question"""
        try:
            # Get first question from backend
            response = await self.api_request(
                "POST", 
                f"/api/interview/start/{self.session_id}"
            )
            
            if response and response.get("success"):
                question_data = response.get("first_question", {})
                self.current_question_id = question_data.get("id")
                question_text = question_data.get("question_text")
                
                self.current_question_index = 1
                
                # Speak the question
                await self.speak(f"Question {self.current_question_index}: {question_text}")
                
                # Start listening for answer
                self.state = InterviewState.QUESTIONING
                
            else:
                await self.speak("I couldn't retrieve the first question. Let me try again.")
                
        except Exception as e:
            logger.error(f"Error starting first question: {e}")
            await self.speak("I'm having trouble retrieving questions. Please wait a moment.")
    
    async def setup_speech_recognition(self, audio_track: Track):
        """Setup continuous speech recognition"""
        if not self.stt:
            logger.warning("STT not available")
            return
            
        try:
            # Create audio source from track
            audio_source = AudioSource(audio_track)
            
            # Start continuous recognition
            async for event in self.stt.recognize_audio(audio_source):
                if event.type == "final_transcript":
                    await self.handle_speech_input(event.transcript)
                    
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
    
    async def handle_speech_input(self, transcript: str):
        """Process speech input from candidate"""
        logger.info(f"Received transcript: {transcript}")
        
        if self.state == InterviewState.QUESTIONING:
            # Candidate is answering a question
            await self.process_answer(transcript)
            
        elif self.state == InterviewState.INTRODUCTION:
            # Check if candidate is ready
            if any(word in transcript.lower() for word in ["yes", "ready", "sure", "okay"]):
                await self.start_first_question()
    
    async def process_answer(self, answer_text: str):
        """Process candidate's answer and move to next question"""
        if not self.current_question_id:
            return
            
        try:
            self.state = InterviewState.EVALUATING
            
            # Submit answer to backend for evaluation
            response = await self.api_request(
                "POST",
                f"/api/interview/{self.session_id}/answer",
                {
                    "question_id": self.current_question_id,
                    "answer_text": answer_text,
                    "duration": 30  # Approximate duration
                }
            )
            
            if response and response.get("success"):
                feedback = response.get("feedback", {})
                next_question = response.get("next_question")
                is_complete = response.get("is_complete", False)
                
                # Provide brief feedback
                feedback_text = feedback.get("feedback_text", "Thank you for your answer.")
                brief_feedback = self.extract_brief_feedback(feedback_text)
                await self.speak(f"Thank you. {brief_feedback}")
                
                if is_complete:
                    await self.complete_interview()
                elif next_question:
                    await self.ask_next_question(next_question)
                else:
                    await self.speak("I'm having trouble retrieving the next question.")
                    
        except Exception as e:
            logger.error(f"Error processing answer: {e}")
            await self.speak("I'm having trouble processing your answer. Could you please repeat it?")
            self.state = InterviewState.QUESTIONING
    
    async def ask_next_question(self, question_data: Dict):
        """Ask the next question"""
        try:
            self.current_question_id = question_data.get("id")
            question_text = question_data.get("question_text")
            self.current_question_index += 1
            
            # Brief pause before next question
            await asyncio.sleep(1)
            
            await self.speak(f"Question {self.current_question_index}: {question_text}")
            
            self.state = InterviewState.QUESTIONING
            
        except Exception as e:
            logger.error(f"Error asking next question: {e}")
    
    async def complete_interview(self):
        """Complete the interview and provide summary"""
        try:
            self.state = InterviewState.COMPLETED
            
            # Get interview summary from backend
            summary = await self.get_interview_summary()
            
            completion_message = f"""
            Thank you for completing the interview! You answered {self.current_question_index} questions.
            
            Your overall performance was good, and detailed feedback will be available shortly.
            
            We'll be in touch with you soon regarding the next steps. Have a great day!
            """
            
            await self.speak(completion_message)
            
        except Exception as e:
            logger.error(f"Error completing interview: {e}")
            await self.speak("Thank you for completing the interview. We'll be in touch soon!")
    
    async def speak(self, text: str):
        """Convert text to speech and play it"""
        try:
            logger.info(f"Speaking: {text[:100]}...")
            
            # Generate TTS audio
            audio_stream = await self.tts.synthesize(text)
            
            # Play audio (implementation depends on LiveKit setup)
            # This would typically involve creating an audio track and publishing it
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
    
    def extract_brief_feedback(self, feedback_text: str) -> str:
        """Extract brief feedback from detailed feedback"""
        # Simple extraction - could be enhanced with NLP
        sentences = feedback_text.split('.')
        if sentences:
            return sentences[0] + "."
        return "Good answer."
    
    async def get_session_info(self) -> Optional[Dict]:
        """Get session information from backend"""
        return await self.api_request("GET", f"/api/interview/session/{self.session_id}")
    
    async def get_interview_summary(self) -> Optional[Dict]:
        """Get interview summary from backend"""
        return await self.api_request("GET", f"/api/interview/summary/{self.session_id}")
    
    async def api_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make API request to backend"""
        try:
            url = f"{BACKEND_URL}{endpoint}"
            
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url) as response:
                        if response.status == 200:
                            return await response.json()
                elif method == "POST":
                    async with session.post(url, json=data) as response:
                        if response.status == 200:
                            return await response.json()
                            
        except Exception as e:
            logger.error(f"API request error: {e}")
        
        return None

# Agent entry point
async def entrypoint(ctx: JobContext):
    """Main entry point for the LiveKit agent"""
    logger.info("Starting Real-Time Voice Interview Agent")
    
    # Initialize agent
    voice_agent = RealTimeVoiceAgent()
    
    # Connect to room
    room = Room()
    
    # Set up event handlers
    @room.on("participant_connected")
    async def on_participant_connected(participant: Participant):
        await voice_agent.on_participant_connected(participant)
    
    @room.on("track_published") 
    async def on_track_published(publication, participant: Participant):
        await voice_agent.on_track_published(publication, participant)
    
    # Connect to room
    await ctx.connect()
    
    logger.info("Voice agent connected and ready")

if __name__ == "__main__":
    agents.run(entrypoint)
