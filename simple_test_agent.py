"""
Simple Test Agent - Just for Voice Testing
This agent will immediately speak when anyone joins
"""

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation, google

load_dotenv()

class SimpleTestAgent(Agent):
    """Very simple agent that just speaks a greeting"""
    
    def __init__(self) -> None:
        super().__init__(
            instructions="""
You are a test AI agent. 

When activated, immediately say: "Hello! This is a test. Can you hear me? I am speaking using Google's voice model through LiveKit."

Then say: "If you can hear this, the voice system is working perfectly!"

Keep it simple and just speak these two sentences.
""",
            llm=google.beta.realtime.RealtimeModel(
                voice="Aoede",
                temperature=0.5,
            ),
        )

async def simple_entrypoint(ctx: agents.JobContext):
    """Simple entry point that starts speaking immediately"""
    
    print("🔊 Simple Test Agent Starting...")
    
    # Create agent session
    session = AgentSession()

    # Start the session
    await session.start(
        room=ctx.room,
        agent=SimpleTestAgent(),
        room_input_options=RoomInputOptions(
            video_enabled=False,  # Keep it simple
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Connect to room
    await ctx.connect()
    print("✅ Connected to LiveKit room")

    # Set up participant detection
    participant_joined = False
    
    @ctx.room.on("participant_connected")
    def on_participant_connected(participant):
        nonlocal participant_joined
        if not participant_joined and not participant.identity.startswith("agent"):
            participant_joined = True
            print(f"🎤 Test: Participant joined: {participant.identity}")
            print("🗣️ Starting to speak...")
            
            # Force the agent to speak immediately
            import asyncio
            asyncio.create_task(session.generate_reply(
                instructions="Start speaking immediately. Say your greeting now."
            ))

if __name__ == "__main__":
    print("🔊 Simple Voice Test Agent")
    print("=" * 40)
    print("This agent will speak immediately when you join")
    print("If you hear nothing, there's a voice plugin issue")
    print()
    print("🚀 Starting simple test agent...")
    
    # Run the simple test agent
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=simple_entrypoint))
