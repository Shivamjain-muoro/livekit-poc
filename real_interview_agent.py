"""
Real-Time AI Interview Agent using LiveKit Agents
=================================================
A professional AI interviewer that joins LiveKit rooms as a real participant
and conducts natural voice interviews with candidates.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

# LiveKit Agents Framework
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import google, silero
from livekit import rtc

# Google AI for conversation
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InterviewSession:
    """Interview session data"""
    candidate_name: str
    position: str
    experience_level: str
    skills: List[str]
    current_question: int = 0
    questions: List[Dict] = None
    answers: List[str] = None
    start_time: datetime = None
    
    def __post_init__(self):
        if self.questions is None:
            self.questions = []
        if self.answers is None:
            self.answers = []
        if self.start_time is None:
            self.start_time = datetime.now()

class AIInterviewer:
    """Real AI Interviewer using LiveKit Agents"""
    
    def __init__(self):
        self.session: Optional[InterviewSession] = None
        self.assistant: Optional[VoiceAssistant] = None
        self.room: Optional[rtc.Room] = None
        
    async def initialize_interview(self, room_name: str, candidate_info: Dict):
        """Initialize interview session with candidate information"""
        try:
            # Extract candidate info from room metadata or participant info
            self.session = InterviewSession(
                candidate_name=candidate_info.get("name", "Candidate"),
                position=candidate_info.get("position", "Software Engineer"),
                experience_level=candidate_info.get("experience_level", "mid"),
                skills=candidate_info.get("skills", [])
            )
            
            # Generate personalized interview questions
            self.session.questions = await self._generate_interview_questions()
            
            logger.info(f"Interview initialized for {self.session.candidate_name}")
            logger.info(f"Generated {len(self.session.questions)} questions")
            
        except Exception as e:
            logger.error(f"Failed to initialize interview: {e}")
            raise
    
    async def _generate_interview_questions(self) -> List[Dict]:
        """Generate personalized interview questions using Google Gemini"""
        if not GOOGLE_API_KEY:
            return self._get_fallback_questions()
        
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            You are a professional technical interviewer. Generate 5 progressive interview questions for:
            
            Candidate: {self.session.candidate_name}
            Position: {self.session.position}
            Experience Level: {self.session.experience_level}
            Skills: {', '.join(self.session.skills)}
            
            Requirements:
            1. Start with a warm introduction question
            2. Include 2-3 technical questions appropriate for {self.session.experience_level} level
            3. Add 1-2 behavioral/situational questions
            4. End with a forward-looking question
            5. Make questions conversational and natural
            6. Ensure difficulty matches experience level
            
            Return as JSON array:
            [
                {{
                    "question_text": "Warm, conversational question here",
                    "question_type": "introduction|technical|behavioral|future",
                    "expected_duration": 120,
                    "follow_up_hints": ["hint1", "hint2"]
                }}
            ]
            
            Make it feel like a real human interviewer asking questions.
            """
            
            response = model.generate_content(prompt)
            questions_data = json.loads(response.text.strip())
            
            logger.info(f"Generated {len(questions_data)} AI-powered questions")
            return questions_data
            
        except Exception as e:
            logger.warning(f"AI question generation failed: {e}, using fallback")
            return self._get_fallback_questions()
    
    def _get_fallback_questions(self) -> List[Dict]:
        """High-quality fallback questions"""
        return [
            {
                "question_text": f"Hi {self.session.candidate_name}! Thanks for joining today. Could you start by telling me a bit about yourself and what excites you most about the {self.session.position} role?",
                "question_type": "introduction",
                "expected_duration": 120,
                "follow_up_hints": ["background", "motivation", "interests"]
            },
            {
                "question_text": "That's great! Now, I'd love to hear about a challenging technical project you've worked on recently. Could you walk me through the problem, your approach, and what you learned?",
                "question_type": "technical",
                "expected_duration": 150,
                "follow_up_hints": ["problem-solving", "technical depth", "learning"]
            },
            {
                "question_text": f"Excellent. Looking at your skills in {', '.join(self.session.skills[:3]) if self.session.skills else 'your technical areas'}, can you give me a specific example of how you've applied these in a real project?",
                "question_type": "technical",
                "expected_duration": 140,
                "follow_up_hints": ["practical application", "real examples", "impact"]
            },
            {
                "question_text": "I'm curious about your teamwork style. Can you tell me about a time when you had to collaborate with a difficult team member or resolve a conflict? How did you handle it?",
                "question_type": "behavioral",
                "expected_duration": 130,
                "follow_up_hints": ["interpersonal skills", "conflict resolution", "leadership"]
            },
            {
                "question_text": f"Finally, where do you see yourself growing in your {self.session.position} career over the next 2-3 years? What kind of challenges are you looking forward to?",
                "question_type": "future",
                "expected_duration": 100,
                "follow_up_hints": ["career goals", "growth mindset", "company alignment"]
            }
        ]
    
    async def create_voice_assistant(self, ctx: JobContext) -> VoiceAssistant:
        """Create the voice assistant with proper speech processing"""
        
        # Initialize speech services
        try:
            # Use Google Speech services if available, fallback to Silero
            if GOOGLE_API_KEY:
                stt = google.STT(language="en-US")
                tts = google.TTS(voice="en-US-Neural2-A")  # Professional female voice
                logger.info("Using Google Speech services")
            else:
                stt = silero.STT()
                tts = silero.TTS()
                logger.info("Using Silero speech services")
        except Exception as e:
            logger.warning(f"Speech service initialization failed: {e}, using defaults")
            stt = silero.STT()
            tts = silero.TTS()
        
        # Create the initial prompt for the AI
        initial_prompt = self._create_interviewer_prompt()
        
        # Create voice assistant
        assistant = VoiceAssistant(
            vad=silero.VAD.load(),  # Voice Activity Detection
            stt=stt,  # Speech to Text
            llm=llm.LLM.create(
                model="gpt-3.5-turbo",  # Can be replaced with local models
                temperature=0.7,
                system_prompt=initial_prompt
            ),
            tts=tts,  # Text to Speech
            chat_ctx=llm.ChatContext(),
            will_synthesize_assistant_reply=True
        )
        
        return assistant
    
    def _create_interviewer_prompt(self) -> str:
        """Create the system prompt for the AI interviewer"""
        return f"""
        You are a professional, friendly AI interviewer conducting a live interview with {self.session.candidate_name} 
        for a {self.session.position} position. They have {self.session.experience_level} level experience.
        
        Your personality:
        - Professional but warm and conversational
        - Encouraging and supportive
        - Genuinely interested in their responses
        - Ask natural follow-up questions
        - Keep responses concise and interview-focused
        
        Current interview context:
        - Position: {self.session.position}
        - Experience Level: {self.session.experience_level}
        - Skills: {', '.join(self.session.skills)}
        - Question {self.session.current_question + 1} of {len(self.session.questions)}
        
        Guidelines:
        1. Ask one question at a time
        2. Listen carefully to their full response
        3. Ask natural follow-up questions when appropriate
        4. Keep your responses conversational (30-60 seconds)
        5. Acknowledge their answers positively
        6. Move naturally between questions
        7. End with next steps if this is the final question
        
        Start by asking the first question naturally, as if this is a real interview.
        Current question: {self.session.questions[0]['question_text'] if self.session.questions else "Tell me about yourself."}
        """
    
    async def handle_interview_flow(self, assistant: VoiceAssistant):
        """Handle the natural flow of the interview"""
        
        # Start the interview
        logger.info("Starting interview conversation")
        
        # The assistant will handle the conversation flow automatically
        # We can add custom handlers for specific interview logic
        
        @assistant.on("user_speech_committed")
        async def on_user_response(assistant: VoiceAssistant, user_msg: str):
            """Handle when user completes their response"""
            logger.info(f"Candidate response: {user_msg[:100]}...")
            
            # Store the answer
            self.session.answers.append(user_msg)
            
            # Check if we should move to next question
            if len(self.session.answers) >= len(self.session.questions):
                logger.info("Interview completed - all questions answered")
                await assistant.say("Thank you for your time today! That completes our interview. We'll be in touch with next steps soon.")
                return
            
            # Update context for next question
            self.session.current_question = len(self.session.answers)
            if self.session.current_question < len(self.session.questions):
                next_question = self.session.questions[self.session.current_question]
                logger.info(f"Moving to question {self.session.current_question + 1}: {next_question['question_text'][:50]}...")


async def entrypoint(ctx: JobContext):
    """Main entry point for the LiveKit Agent"""
    logger.info("AI Interviewer Agent starting...")
    
    # Wait for participant to join
    await ctx.wait_for_participant()
    logger.info("Candidate joined the interview room")
    
    # Get participant information (from room metadata or participant metadata)
    participants = ctx.room.remote_participants
    candidate_info = {}
    
    if participants:
        participant = list(participants.values())[0]
        # Try to get candidate info from participant metadata
        if hasattr(participant, 'metadata') and participant.metadata:
            try:
                candidate_info = json.loads(participant.metadata)
            except:
                pass
        
        # Fallback to basic info
        candidate_info.setdefault("name", participant.identity or "Candidate")
        candidate_info.setdefault("position", "Software Engineer")
        candidate_info.setdefault("experience_level", "mid")
        candidate_info.setdefault("skills", ["Python", "JavaScript"])
    
    logger.info(f"Candidate info: {candidate_info}")
    
    # Initialize AI Interviewer
    interviewer = AIInterviewer()
    await interviewer.initialize_interview(ctx.room.name, candidate_info)
    
    # Create voice assistant
    assistant = await interviewer.create_voice_assistant(ctx)
    
    # Set up interview flow handling
    await interviewer.handle_interview_flow(assistant)
    
    # Start the voice assistant
    assistant.start(ctx.room)
    
    logger.info("AI Interviewer is now active and ready to conduct the interview")
    
    # Keep the agent alive
    await assistant.aclose()


if __name__ == "__main__":
    # Run the LiveKit Agent
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            auto_subscribe=AutoSubscribe.AUDIO_ONLY,  # Only subscribe to audio
        )
    )
