"""
LiveKit Voice Agent Worker
=========================
This worker handles the real voice AI interview agent with actual speech processing.
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

# LiveKit agents imports
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.agents.llm import ChatContext
from livekit import rtc

# Voice processing plugins
from livekit.plugins import openai, deepgram, silero

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

async def entrypoint(ctx: JobContext):
    """Main entry point for voice AI interviewer agent"""
    logger.info(f"🎙️ REAL Voice AI Interviewer starting for room: {ctx.room.name}")
    
    # Configure voice processing based on available services
    if OPENAI_API_KEY:
        logger.info("🎤 Using OpenAI for premium voice services")
        stt = openai.STT()
        llm = openai.LLM(model="gpt-4o-mini")
        tts = openai.TTS(voice="alloy")  # Professional voice
    elif DEEPGRAM_API_KEY:
        logger.info("🎤 Using Deepgram STT + Silero TTS")
        stt = deepgram.STT()
        llm = openai.LLM(model="gpt-3.5-turbo")  # Fallback model
        tts = silero.TTS()
    else:
        logger.info("🎤 Using Silero for free voice services")
        # Note: You might need an OpenAI key for LLM even with free voice
        stt = silero.STT()
        llm = openai.LLM(model="gpt-3.5-turbo") if OPENAI_API_KEY else None
        tts = silero.TTS()
    
    if not llm:
        logger.error("❌ No LLM available. Please set OPENAI_API_KEY.")
        return
    
    # Create interview context
    interview_prompt = """You are a professional AI interviewer conducting a job interview.

Your personality:
- Warm, friendly, and professional
- Encouraging and supportive
- Great listener who asks thoughtful follow-up questions
- Naturally conversational, not robotic

Interview structure:
1. Welcome the candidate warmly and put them at ease
2. Ask about their background and what interests them about the role
3. Explore their technical experience and projects they're proud of
4. Discuss challenges they've overcome and how they work in teams
5. Talk about their career goals and what they're looking for
6. Wrap up with next steps and thank them

Guidelines:
- Keep responses under 30 seconds
- Ask one question at a time
- Show genuine interest in their answers
- Use their name occasionally to personalize
- Be encouraging and positive
- Ask follow-up questions based on their responses
- Make it feel like a natural conversation, not an interrogation

Remember: This is a real person with feelings. Make them feel comfortable and confident."""

    # Create voice assistant with real capabilities
    assistant = VoiceAssistant(
        vad=rtc.VAD(
            min_speaking_duration=0.8,   # Minimum speech duration to register
            min_silence_duration=1.2,    # Silence before stopping listening
            max_buffered_speech=30.0,    # Max continuous speech
            activation_threshold=0.5,    # Voice activation sensitivity
            deactivation_threshold=0.3   # Voice deactivation sensitivity
        ),
        stt=stt,
        llm=llm,
        tts=tts,
        chat_ctx=ChatContext().append(
            role="system",
            text=interview_prompt
        ),
        # Advanced voice assistant settings
        interrupt_speech_duration=1.0,   # Allow interruptions after 1 second
        preemptive_synthesis=True,       # Start generating speech early for faster response
        transcription_speed=2.0,         # Faster transcription processing
        allow_interruptions=True,        # Allow candidate to interrupt AI
        transcription_silence_timeout=2.0  # Stop transcribing after 2s silence
    )
    
    logger.info("🎯 Voice assistant configured with REAL voice processing")
    
    # Start the assistant
    assistant.start(ctx.room)
    
    # Handle participant events
    @ctx.room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant):
        if not participant.identity.startswith("voice_assistant"):
            logger.info(f"👋 Candidate joined interview: {participant.identity}")
            # The assistant will automatically start the conversation
    
    @ctx.room.on("participant_disconnected")
    def on_participant_disconnected(participant: rtc.RemoteParticipant):
        logger.info(f"👋 Participant left interview: {participant.identity}")
    
    # Keep the agent running
    await assistant.aclose()

if __name__ == "__main__":
    # Run the LiveKit agent worker
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            # Worker configuration
            ws_url=os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
            api_key=os.getenv("LIVEKIT_API_KEY", "devkey"),
            api_secret=os.getenv("LIVEKIT_API_SECRET", "secret"),
            # Agent identity
            agent_name="voice_ai_interviewer"
        )
    )
