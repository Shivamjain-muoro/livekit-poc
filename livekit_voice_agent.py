"""
Pure LiveKit Voice Agent Interview System
========================================
Uses ONLY LiveKit agents for voice interaction - no browser APIs, no WebSocket workarounds
"""

import asyncio
import logging
import os
from typing import Dict, List
from dataclasses import dataclass
from dotenv import load_dotenv

# Core LiveKit imports
from livekit import rtc
from livekit.agents import (
    AutoSubscribe, 
    JobContext, 
    JobProcess, 
    WorkerOptions, 
    cli,
    JobRequest
)
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import openai, silero
from livekit.agents.llm import (
    ChatContext, 
    ChatMessage,
    ChatRole
)

# AI for interview questions
import google.generativeai as genai

load_dotenv()

# Configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure AI
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InterviewCandidate:
    name: str
    position: str
    experience_years: int
    skills: List[str]

class AIInterviewer:
    """AI Interviewer using LiveKit Voice Assistant"""
    
    def __init__(self, candidate: InterviewCandidate):
        self.candidate = candidate
        self.questions = []
        self.current_question = 0
        self.max_questions = 5
        self.generate_interview_questions()
        
    def generate_interview_questions(self):
        """Generate personalized interview questions"""
        if GEMINI_API_KEY:
            try:
                model = genai.GenerativeModel('gemini-pro')
                prompt = f"""Generate 5 excellent interview questions for a {self.candidate.position} position.

Candidate Profile:
- Name: {self.candidate.name}
- Experience: {self.candidate.experience_years} years
- Skills: {', '.join(self.candidate.skills)}

Requirements:
- Mix of behavioral, technical, and situational questions
- Personalized to their experience level and skills
- Conversational and engaging tone
- Allow for detailed responses

Return ONLY the questions as a simple list, one per line."""
                
                response = model.generate_content(prompt)
                self.questions = [q.strip() for q in response.text.strip().split('\n') if q.strip()][:5]
                
            except Exception as e:
                logger.warning(f"AI question generation failed: {e}")
                self.questions = self.get_fallback_questions()
        else:
            self.questions = self.get_fallback_questions()
            
    def get_fallback_questions(self) -> List[str]:
        """Fallback interview questions"""
        return [
            f"Tell me about yourself and what draws you to the {self.candidate.position} role.",
            f"With {self.candidate.experience_years} years of experience, describe a challenging project you're proud of.",
            "How do you handle working in a team environment when facing disagreements?",
            f"Can you give me a specific example of how you've used {', '.join(self.candidate.skills[:2])}?",
            f"Where do you see yourself growing in the {self.candidate.position} field over the next few years?"
        ]
    
    def get_system_prompt(self) -> str:
        """Get the AI interviewer system prompt"""
        return f"""You are a professional AI interviewer conducting a {self.candidate.position} interview for {self.candidate.name}.

Candidate Information:
- Name: {self.candidate.name}
- Position: {self.candidate.position}  
- Experience: {self.candidate.experience_years} years
- Skills: {', '.join(self.candidate.skills)}

Your Role:
- Be professional, friendly, and encouraging
- Ask thoughtful follow-up questions based on responses
- Keep responses conversational and under 30 seconds when speaking
- Guide the interview naturally through the prepared questions
- Listen actively and show genuine interest in their responses

Interview Questions to Ask:
{chr(10).join([f"{i+1}. {q}" for i, q in enumerate(self.questions)])}

Current Status: Ready to start the interview

Instructions:
- Start with a warm welcome
- Ask the prepared questions one by one
- Listen to their full response before moving to the next question
- Provide encouraging feedback between questions
- Keep the conversation natural and flowing
- End with professional next steps

Remember: This is a REAL voice conversation using LiveKit agents. Speak naturally and be genuinely interested in learning about the candidate."""

async def entrypoint(ctx: JobContext):
    """LiveKit agent entrypoint for voice interview"""
    
    logger.info(f"🎙️ Starting LiveKit voice interview agent")
    
    # Wait for participant to join
    await ctx.wait_for_participant()
    participant = ctx.room.remote_participants[list(ctx.room.remote_participants.keys())[0]]
    
    logger.info(f"✅ Participant joined: {participant.name or participant.identity}")
    
    # Parse candidate info from participant metadata or identity
    # For demo, using default candidate info
    candidate = InterviewCandidate(
        name=participant.name or participant.identity or "Candidate",
        position="Software Developer",
        experience_years=3,
        skills=["Python", "JavaScript", "React", "Node.js"]
    )
    
    # Create AI interviewer
    interviewer = AIInterviewer(candidate)
    
    # Initialize voice assistant with LiveKit plugins
    assistant = VoiceAssistant(
        vad=silero.VAD.load(),  # Voice activity detection
        stt=openai.STT(),       # Speech-to-text
        llm=openai.LLM(         # Large language model
            model="gpt-4-turbo-preview",
            temperature=0.7,
        ),
        tts=openai.TTS(         # Text-to-speech
            voice="alloy",
            speed=1.0,
        ),
        chat_ctx=ChatContext([
            ChatMessage(
                role=ChatRole.SYSTEM,
                content=interviewer.get_system_prompt()
            )
        ])
    )
    
    # Start the voice assistant
    assistant.start(ctx.room, participant)
    
    # Send initial welcome message
    await assistant.say(
        f"Hello {candidate.name}! Welcome to your {candidate.position} interview. "
        f"I'm excited to learn more about you today. Let's begin!"
    )
    
    # Wait a moment, then start with first question
    await asyncio.sleep(2)
    
    if interviewer.questions:
        await assistant.say(interviewer.questions[0])
    
    logger.info("🎙️ Voice interview started - AI assistant is now active")

if __name__ == "__main__":
    # Run LiveKit agent
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=None,
        )
    )
