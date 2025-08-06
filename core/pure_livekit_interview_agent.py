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
from .interview_prompts import INTERVIEWER_INSTRUCTION, SESSION_INSTRUCTION
from .interview_tools import (
    generate_interview_questions,
    evaluate_candidate_response,
    get_candidate_profile,
    save_interview_response,
    complete_interview_session
)

load_dotenv()

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
    
    print("🎯 ENTRYPOINT: Starting LiveKit agent session...")
    
    try:
        # Connect to the LiveKit room first
        await ctx.connect()
        print("✅ ENTRYPOINT: Connected to room successfully")
        
        # Create the interview agent
        interview_agent = InterviewAgent()
        print("🤖 ENTRYPOINT: Created InterviewAgent with tools and instructions")
        
        # Create session associated with the room context - CORRECT METHOD
        session = ctx.new_agent_session(
            agent=interview_agent,
            room_input_options=RoomInputOptions(
                video_enabled=True,
                noise_cancellation=noise_cancellation.BVC(),
            ),
        )
        
        # Start the session - THIS KEEPS THE AGENT ALIVE AND CONNECTED
        print("🚀 ENTRYPOINT: Starting agent session (this will keep the agent connected)...")
        await session.start()
        
        print("✅ ENTRYPOINT: Agent session started successfully")
        
    except Exception as e:
        print(f"❌ ENTRYPOINT: Error occurred: {e}")
        import traceback
        traceback.print_exc()

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