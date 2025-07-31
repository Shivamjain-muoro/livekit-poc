"""
Pure LiveKit Voice AI Interview A        session = agents.AgentSession(
            instructions=INTERVIEWER_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                model="gemini-2.0-flash-live-001",  # Explicit model for voice
                voice="Aoede",  # Professional female voice
                temperature=0.7,  # Balanced creativity and consistency
                api_key=google_api_key,  # Explicit API key
            ),
            tools=[
                generate_interview_questions,
                evaluate_candidate_response,
                get_candidate_profile,
                save_interview_response,
                complete_interview_session
            ],
        )g the exact pattern from Friday/Jarvis repo
Uses ONLY LiveKit Agents framework - no browser APIs, no WebSockets
"""

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    noise_cancellation,
)
from livekit.plugins import google
import google.generativeai as genai
import os
from interview_prompts import INTERVIEWER_INSTRUCTION, SESSION_INSTRUCTION
from interview_tools import (
    generate_interview_questions,
    evaluate_candidate_response,
    get_candidate_profile,
    save_interview_response,
    complete_interview_session
)

load_dotenv(os.path.join('..', 'config', '.env'))  # Load from config folder
if not os.getenv("GOOGLE_API_KEY"):
    load_dotenv('config/.env')  # Alternative path
if not os.getenv("GOOGLE_API_KEY"):
    load_dotenv()  # Fallback to current directory

# Configure Google API
google_api_key = os.getenv("GOOGLE_API_KEY")
if google_api_key:
    genai.configure(api_key=google_api_key)
    print(f"✅ Google API configured with key: {google_api_key[:8]}...")
else:
    print("❌ GOOGLE_API_KEY not found in environment")

class InterviewAgent(Agent):
    """Pure LiveKit Interview Agent - Follows Friday/Jarvis Pattern"""
    
    def __init__(self) -> None:
        print("🔧 AGENT: Initializing InterviewAgent with tools and instructions...")
        super().__init__(
            instructions=INTERVIEWER_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                voice="Aoede",  # Professional female voice
                temperature=0.7,  # Balanced creativity and consistency
            ),
            tools=[
                generate_interview_questions,
                evaluate_candidate_response,
                get_candidate_profile,
                save_interview_response,
                complete_interview_session
            ],
        )
        print("✅ AGENT: InterviewAgent initialized successfully!")
        print("🛠️ AGENT: Tools configured:")
        print("   - generate_interview_questions")
        print("   - evaluate_candidate_response") 
        print("   - get_candidate_profile")
        print("   - save_interview_response")
        print("   - complete_interview_session")

async def entrypoint(ctx: agents.JobContext):
    """LiveKit Agent Entry Point - Pure LiveKit Implementation"""
    
    print("🎯 ENTRYPOINT: Creating LiveKit agent session...")
    
    # Create the interview agent with proper configuration
    interview_agent = InterviewAgent()
    print("🤖 ENTRYPOINT: Created InterviewAgent with tools and instructions")
    
    # Create agent session 
    session = agents.AgentSession()
    
    # Start the session
    print("🚀 ENTRYPOINT: Starting agent session...")
    await session.start(
        room=ctx.room,
        agent=interview_agent,  # Pass the configured agent
        room_input_options=RoomInputOptions(
            # Enable video for full interview experience
            video_enabled=True,
            # LiveKit enhanced noise cancellation for clear audio
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Connect to the LiveKit room
    print("🔗 ENTRYPOINT: Connecting to LiveKit room...")
    await ctx.connect()
    print("✅ ENTRYPOINT: Connected to room successfully")

    # Simple approach: wait a moment for participants, then start speaking
    import asyncio
    await asyncio.sleep(3)  # Give more time for full connection
    
    # Check if we have participants (excluding the agent)
    participants = [p for p in ctx.room.remote_participants.values() 
                   if not p.identity.startswith("ai_") and not p.identity.startswith("agent")]
    
    if participants:
        print(f"🎤 Found participant(s): {[p.identity for p in participants]}")
        print("🤖 Starting interview conversation...")
        print("🔄 Agent should now be able to call interview tools...")
        
        # The AgentSession with Google Realtime model should automatically start responding
        # when it receives the session instructions. Let's just wait for the natural flow.
        print("🔄 Waiting for AI to begin speaking based on session instructions...")
    else:
        print("⏳ Waiting for participants to join...")

if __name__ == "__main__":
    """
    Run the Pure LiveKit Interview Agent
    This follows the exact same pattern as Friday/Jarvis
    """
    print("🎙️ Starting Pure LiveKit Interview Agent")
    print("=" * 50)
    print("✅ Uses ONLY LiveKit Agents framework")
    print("✅ Real-time voice processing via LiveKit")
    print("✅ AI-powered interview questions and evaluation")
    print("✅ Professional interview experience")
    print("")
    print("❌ NO browser APIs")
    print("❌ NO WebSockets") 
    print("❌ NO simulations")
    print("")
    print("🚀 Starting agent...")
    
    # Run the LiveKit agent using the CLI
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
