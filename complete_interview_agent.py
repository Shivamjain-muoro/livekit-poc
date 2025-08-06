"""
Complete Working LiveKit Interview Agent
All components in one file for easy testing
"""

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, RoomInputOptions, function_tool, RunContext
from livekit.plugins import noise_cancellation, google
import google.generativeai as genai
import os
import json
import sqlite3
import logging
import asyncio
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure Google API
google_api_key = os.getenv("GOOGLE_API_KEY")
if google_api_key:
    genai.configure(api_key=google_api_key)
    print(f"✅ Google API configured with key: {google_api_key[:8]}...")
else:
    print("❌ GOOGLE_API_KEY not found in environment")

# Configure logging
logging.basicConfig(level=logging.INFO)

# INTELLIGENT FAST INTERVIEW PROMPTS
INTERVIEWER_INSTRUCTION = """
# INTELLIGENT AI INTERVIEWER
You are a professional AI interviewer conducting natural, flowing voice interviews.

# IMMEDIATE START PROTOCOL
When a candidate joins, IMMEDIATELY start with:
"Hello! I'm your AI interviewer today. I'm excited to learn about your background and experience. Let's begin our conversation."

# NATURAL CONVERSATION STYLE
- Be warm, professional, and genuinely interested
- Ask follow-up questions based on their responses
- Keep responses conversational but focused (30-50 words)
- Show engagement: "That's interesting," "Tell me more about," "How did you handle"
- Use natural transitions between topics
- Ask one question at a time and listen actively

# INTELLIGENT INTERVIEW FLOW
- Start with background and experience
- Explore their technical skills naturally
- Discuss specific projects they mention
- Ask behavioral questions about challenges and teamwork
- Adapt questions based on their responses
- End with career goals and questions for you

# RESPONSE GUIDELINES
- Keep responses natural and engaging (not too short, not too long)
- Show genuine curiosity about their answers
- Use encouraging phrases: "That sounds challenging," "Great example"
- Build on what they say rather than following a script
- Maintain professional but friendly tone throughout
- Ask clarifying questions when needed

# SPEED OPTIMIZATIONS
- Use minimal tools (only when essential)
- Keep database operations lightweight
- Focus on conversation flow over data storage
- Prioritize natural dialogue over comprehensive evaluation
"""

# DATABASE HELPER
def get_db_path():
    """Get the correct database path"""
    os.makedirs("database", exist_ok=True)
    return os.path.join("database", "interview_sessions.db")

# LIGHTWEIGHT TOOLS FOR SPEED
@function_tool()
async def get_candidate_profile(context: RunContext, session_id: str = "default_session") -> str:
    """Get or create basic candidate profile - lightweight for speed."""
    print(f"⚡ FAST_TOOL: get_candidate_profile called - Session: {session_id}")
    
    # Simple in-memory profile (no database for speed)
    profile = {
        "name": "Interview Candidate",
        "position": "Software Developer",
        "experience_level": "mid-level",
        "skills": "Programming, Problem-solving, Communication",
        "session_id": session_id,
        "interview_type": "technical"
    }
    
    print(f"✅ FAST_TOOL: Created lightweight profile")
    return json.dumps(profile)

@function_tool()
async def generate_interview_questions(
    context: RunContext,
    candidate_name: str,
    position: str,
    experience_level: str,
    skills: str
) -> str:
    """Generate personalized interview questions - optimized for speed."""
    print(f"⚡ FAST_TOOL: generate_interview_questions for {candidate_name}")
    
    try:
        if google_api_key:
            print("🤖 FAST_TOOL: Using Google AI for intelligent questions")
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # OPTIMIZED prompt for faster generation
            prompt = f"""Generate 4 excellent interview questions for a {position}.

Profile: {candidate_name}, {experience_level}, skills: {skills}

Requirements:
- Conversational and engaging
- Mix: background, technical, behavioral, goals
- Natural flow for voice interview

Return as simple JSON array."""
            
            # SPEED OPTIMIZED generation settings
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.3,  # Faster than 0.7, natural than 0.2
                    max_output_tokens=400,  # Limited for speed
                    top_p=0.9
                )
            )
            
            questions_text = response.text.strip()
            
            # Fast parsing
            if '[' in questions_text and ']' in questions_text:
                start = questions_text.find('[')
                end = questions_text.rfind(']') + 1
                questions_json = questions_text[start:end]
                questions = json.loads(questions_json)
            else:
                questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
            
            print(f"✅ FAST_TOOL: Generated {len(questions)} questions quickly")
            return json.dumps(questions)
        
        else:
            # Intelligent fallback questions
            fallback_questions = [
                f"Tell me about your background and what draws you to {position} roles.",
                f"With your {experience_level} experience, describe a project you're particularly proud of.",
                "How do you approach solving complex technical problems?",
                f"Where do you see your {position} career heading in the next few years?"
            ]
            
            print(f"✅ FAST_TOOL: Using smart fallback questions")
            return json.dumps(fallback_questions)
            
    except Exception as e:
        print(f"❌ FAST_TOOL: Error generating questions: {e}")
        return json.dumps([
            "Tell me about your background and experience.",
            "What's a challenging project you've worked on?",
            "How do you work with teams?",
            "What are your career goals?"
        ])

@function_tool()
async def quick_response_note(
    context: RunContext,
    question: str,
    candidate_response: str,
    interviewer_comment: str = ""
) -> str:
    """Quick note-taking without heavy processing - for speed."""
    print(f"⚡ FAST_TOOL: quick_response_note - Question: {question[:30]}...")
    print(f"📝 FAST_TOOL: Response length: {len(candidate_response)} chars")
    
    # Simple evaluation without complex AI processing
    response_quality = "good"
    if len(candidate_response) > 150:
        response_quality = "detailed"
    elif len(candidate_response) < 50:
        response_quality = "brief"
    
    note = {
        "question": question,
        "response_length": len(candidate_response),
        "quality": response_quality,
        "interviewer_comment": interviewer_comment,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"✅ FAST_TOOL: Quick note created ({response_quality} response)")
    return json.dumps(note)

# INTERVIEW AGENT CLASS
class InterviewAgent(Agent):
    """High-Speed LiveKit Interview Agent - Optimized for Fast Responses"""
    
    def __init__(self) -> None:
        print("� FAST_AGENT: Initializing High-Speed InterviewAgent...")
        print("⚡ FAST_AGENT: Optimized for minimal latency...")
        print("🔧 FAST_AGENT: Setting up fast tools (no database)...")
        
        super().__init__(
            instructions=INTERVIEWER_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                voice="Aoede",
                temperature=0.4,  # BALANCED: Natural conversation but faster than 0.7
            ),
            tools=[
                get_candidate_profile,      # Lightweight profile
                generate_interview_questions, # AI-generated but optimized
                quick_response_note,        # Simple note-taking
            ],
        )
        print("✅ FAST_AGENT: High-speed agent initialized!")
        print("🛠️ FAST_AGENT: Tools configured (MINIMAL SET):")
        print("   - quick_acknowledge (instant feedback)")
        print("   - get_next_question (pre-defined, no AI generation)")
        print(f"⚡ FAST_AGENT: Temperature: 0.2 (optimized for speed)")
        print(f"🎯 FAST_AGENT: Tools count: {len(self.tools)} (minimal for speed)")
        print("🚫 FAST_AGENT: NO database operations for maximum speed")
    
    async def on_enter(self) -> None:
        """Called when the task is entered"""
        print("🎬 FAST_AGENT: on_enter() called - Starting high-speed session")
        await super().on_enter()
        print("✅ FAST_AGENT: on_enter() completed - Ready for fast interview")
    
    async def on_exit(self) -> None:
        """Called when the task is exited"""
        print("🎬 FAST_AGENT: on_exit() called - Ending high-speed session")
        await super().on_exit()
        print("✅ FAST_AGENT: on_exit() completed")
    
    async def on_user_turn_completed(self, turn_ctx, new_message) -> None:
        """Called when the user has finished speaking"""
        print(f"🎤 FAST_AGENT: on_user_turn_completed() - Fast processing")
        print(f"📝 FAST_AGENT: Message length: {len(new_message.content)} chars")
        await super().on_user_turn_completed(turn_ctx, new_message)
        print("⚡ FAST_AGENT: Turn processed at high speed")

# ENTRYPOINT FUNCTION
async def entrypoint(ctx: agents.JobContext):
    """LiveKit Agent Entry Point - Complete Working Implementation"""
    
    print("🎯 ENTRYPOINT: Starting LiveKit agent session...")
    print(f"📋 ENTRYPOINT: Job ID: {ctx.job.id}")
    print(f"📋 ENTRYPOINT: Room Name: {ctx.room.name}")
    print(f"📋 ENTRYPOINT: Worker ID: {ctx.worker_id}")
    
    try:
        # Check room state before connecting
        print(f"🔍 ENTRYPOINT: Room state before connect - Name: {ctx.room.name}")
        print(f"🔍 ENTRYPOINT: Room participants before connect: {len(ctx.room.remote_participants)}")
        for pid, participant in ctx.room.remote_participants.items():
            print(f"  👤 Existing participant: {participant.identity} (ID: {pid})")
        
        # Connect to the LiveKit room first
        print("🔗 ENTRYPOINT: Attempting to connect to room...")
        await ctx.connect()
        print("✅ ENTRYPOINT: Connected to room successfully")
        
        # Check room state after connecting
        print(f"🔍 ENTRYPOINT: Room state after connect - Name: {ctx.room.name}")
        print(f"🔍 ENTRYPOINT: Room participants after connect: {len(ctx.room.remote_participants)}")
        for pid, participant in ctx.room.remote_participants.items():
            print(f"  👤 Connected participant: {participant.identity} (ID: {pid})")
        
        # Check if participants are already in the room
        existing_participants = list(ctx.room.remote_participants.values())
        if existing_participants:
            print(f"✅ ENTRYPOINT: Found {len(existing_participants)} existing participant(s):")
            for participant in existing_participants:
                print(f"  👤 Participant: {participant.identity}")
            participant = existing_participants[0]  # Use first participant
        else:
            # Wait for a participant to join
            print("👥 ENTRYPOINT: No existing participants, waiting for participant to join...")
            print("⏳ ENTRYPOINT: This will block until someone joins the room...")
            try:
                participant = await ctx.wait_for_participant()
                print(f"✅ ENTRYPOINT: Participant joined: {participant.identity}")
                print(f"📋 ENTRYPOINT: Participant details - Name: {participant.name}, Kind: {participant.kind}")
            except Exception as wait_error:
                print(f"❌ ENTRYPOINT: Error waiting for participant: {wait_error}")
                raise
        
        # Double-check room state
        current_participants = list(ctx.room.remote_participants.values())
        print(f"🔍 ENTRYPOINT: Current room state - {len(current_participants)} participant(s)")
        for p in current_participants:
            print(f"  👤 Active participant: {p.identity} - {p.name}")
        
        # Create the interview agent
        print("🤖 ENTRYPOINT: Creating InterviewAgent with tools and instructions...")
        interview_agent = InterviewAgent()
        print("✅ ENTRYPOINT: InterviewAgent created successfully")
        
        # CORRECT LIVEKIT PATTERN: Create AgentSession and start it
        print("🚀 ENTRYPOINT: Creating AgentSession...")
        
        # Import voice module to get AgentSession
        from livekit.agents.voice import AgentSession
        
        # Create agent session with detailed logging
        print("🔧 ENTRYPOINT: Instantiating AgentSession object...")
        agent_session = AgentSession()
        print("✅ ENTRYPOINT: AgentSession object created")
        
        # Start the session with the agent and room
        print("🎤 ENTRYPOINT: Starting agent session (this will keep the agent connected)...")
        print(f"🎤 ENTRYPOINT: Room for session: {ctx.room.name}")
        print(f"🎤 ENTRYPOINT: Agent for session: {interview_agent}")
        
        try:
            await agent_session.start(interview_agent, room=ctx.room)
            print("✅ ENTRYPOINT: Agent session started successfully!")
        except Exception as start_error:
            print(f"❌ ENTRYPOINT: Error starting agent session: {start_error}")
            raise
        
        # Keep the session alive by monitoring room events
        print("🔄 ENTRYPOINT: Monitoring room for participants...")
        print("🔄 ENTRYPOINT: Agent will stay active as long as participants are in the room")
        
        # Monitor room state continuously
        check_count = 0
        while True:
            check_count += 1
            participants = list(ctx.room.remote_participants.values())
            print(f"🔄 ENTRYPOINT: Check #{check_count} - Found {len(participants)} participant(s)")
            
            if len(participants) == 0:
                print("👋 ENTRYPOINT: All participants left, ending session...")
                break
            
            # Log participant details every few checks
            if check_count % 6 == 1:  # Every 30 seconds (5s * 6)
                for p in participants:
                    print(f"  👤 Active participant: {p.identity} - SID: {p.sid}")
                    print(f"  📊 Participant tracks: {len(p.track_publications)} published")
                    print(f"  🔗 Participant kind: {p.kind}")
            
            # Wait a bit before checking again
            print(f"⏸️ ENTRYPOINT: Waiting 5 seconds before next check...")
            await asyncio.sleep(5)
        
        # Close the agent session
        print("🔚 ENTRYPOINT: Closing agent session...")
        try:
            await agent_session.aclose()
            print("✅ ENTRYPOINT: Agent session closed successfully")
        except Exception as close_error:
            print(f"⚠️ ENTRYPOINT: Error closing agent session: {close_error}")
        
        print("✅ ENTRYPOINT: Agent session completed")
        print("🎤 ENTRYPOINT: Interview session finished!")
        
    except Exception as e:
        print(f"❌ ENTRYPOINT: Error occurred: {e}")
        print(f"❌ ENTRYPOINT: Error type: {type(e).__name__}")
        import traceback
        print("❌ ENTRYPOINT: Full traceback:")
        traceback.print_exc()
        
        # Try to get more context about the room state during error
        try:
            print(f"🔍 ENTRYPOINT: Room state during error - Name: {ctx.room.name}")
            print(f"🔍 ENTRYPOINT: Participants during error: {len(ctx.room.remote_participants)}")
        except Exception as debug_error:
            print(f"❌ ENTRYPOINT: Could not get room state: {debug_error}")

# MAIN EXECUTION
if __name__ == "__main__":
    """
    Run the Complete LiveKit Interview Agent
    """
    print("🎙️ Starting INTELLIGENT FAST LiveKit Interview Agent")
    print("=" * 60)
    print("✅ Uses ONLY LiveKit Agents framework")
    print("✅ Real-time voice processing via LiveKit")
    print("🤖 AI-powered questions with speed optimization")
    print("� Natural conversation flow (not robotic)")
    print("⚡ FAST but intelligent responses")
    print("🚫 NO heavy database operations")
    print("")
    print("🚀 INTELLIGENT SPEED FEATURES:")
    print("   - Temperature 0.4 (balanced for natural conversation)")
    print("   - AI-generated questions (optimized)")
    print("   - Lightweight tools (no complex evaluations)")
    print("   - Natural response length (30-50 words)")
    print("")
    print("🚀 Starting intelligent fast agent...")
    
    # Run the LiveKit agent using the CLI
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
