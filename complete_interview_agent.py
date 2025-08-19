"""
Enhanced Fast Non-Blocking LiveKit Interview Agent
Real-time conversation with background comprehensive evaluation
"""

from dotenv import load_dotenv
import os

# Load local environment configuration
load_dotenv('config/.env')

print("🏠 MUORO AI INTERVIEWER V0.3.1 STARTING")
print("=" * 50)
print(f"🔗 LiveKit URL: {os.getenv('LIVEKIT_URL')}")
print(f"🔑 API Key: {os.getenv('LIVEKIT_API_KEY')}")
print(f"🤖 Google AI: {'✅ Configured' if os.getenv('GOOGLE_API_KEY') else '❌ Missing'}")
print("=" * 50)

from livekit import agents
from livekit.agents import Agent, AgentSession, RoomInputOptions, function_tool, RunContext
from livekit.plugins import noise_cancellation, google
import google.generativeai as genai
import json
import sqlite3
import logging
import asyncio
from datetime import datetime

# Import REAL-TIME tools with instant response and AUTOMATED evaluation
from realtime_interview_tools import (
    start_interview_session,
    record_candidate_response,
    get_real_time_progress,
    end_interview_session,
    auto_start_session_from_context,
    get_automated_evaluation_summary
)
from fast_interview_tools import (
    ask_interview_question,
    get_quick_feedback
)
from background_evaluator import get_background_evaluator
from report_generator import generate_session_report

# Load environment variables
load_dotenv()

# Configure Google API
google_api_key = os.getenv("GOOGLE_API_KEY")
if google_api_key:
    genai.configure(api_key=google_api_key)
    print(f"✅ Google API configured with key: {google_api_key[:8]}...")
else:
    print("❌ GOOGLE_API_KEY not found in environment")

# Configure detailed logging for interview agent
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('interview_detailed.log'),
        logging.StreamHandler()
    ]
)

# Create logger for this module
logger = logging.getLogger('InterviewAgent')

# ENHANCED FAST NON-BLOCKING INTERVIEW PROMPTS
INTERVIEWER_INSTRUCTION = """
# REAL-TIME AI INTERVIEWER - NATURAL CONVERSATION WITH AUTOMATIC RECORDING

You are Muoro AI interviewer v0.3.1, a professional AI interviewer with ONE CRITICAL REQUIREMENT: RECORD EVERY CONVERSATION EXCHANGE.

## 🚨 CRITICAL: CONVERSATION RECORDING PROTOCOL 🚨
After EVERY substantive response from the candidate, you MUST:
1. Call get_real_time_progress (to get session_id)
2. IMMEDIATELY call record_candidate_response with:
   - session_id: from get_real_time_progress
   - question: YOUR exact question
   - response: Their complete response
   - response_duration: estimate in seconds

THIS IS MANDATORY - NO EXCEPTIONS!

## IMMEDIATE START PROTOCOL
When a candidate joins, start with:
"Hello! I'm your AI interviewer for today's session. Let's begin. Can you tell me your name and a bit about your background?"

## CONVERSATION RECORDING WORKFLOW
1. Ask a question
2. Listen to their response
3. IMMEDIATELY call get_real_time_progress 
4. IMMEDIATELY call record_candidate_response with all details
5. Continue conversation naturally
6. Repeat for EVERY exchange

## EXAMPLE CONVERSATION WITH RECORDING:
You: "Can you tell me your name and background?"
[Candidate responds: "Hi, I'm John. I'm a software developer with 3 years experience..."]
→ IMMEDIATELY call get_real_time_progress
→ IMMEDIATELY call record_candidate_response:
  - session_id: (from get_real_time_progress)
  - question: "Can you tell me your name and background?"
  - response: "Hi, I'm John. I'm a software developer with 3 years experience..."
  - response_duration: 15.0

You: "That's great! What programming languages do you work with?"
[Candidate responds: "I primarily work with Python and JavaScript..."]
→ IMMEDIATELY call get_real_time_progress
→ IMMEDIATELY call record_candidate_response:
  - session_id: (from get_real_time_progress)  
  - question: "What programming languages do you work with?"
  - response: "I primarily work with Python and JavaScript..."
  - response_duration: 12.0

Continue this pattern for EVERY exchange!

## CONVERSATION STYLE
- Be warm, professional, and engaging
- Ask clear, specific questions
- Keep your responses brief (30-50 words)
- Build naturally on their answers
- Show genuine interest
- Ask follow-up questions based on their responses

## INTERVIEW FLOW STRUCTURE
1. **Introduction**: Name, background, current role
2. **Experience**: Previous work, projects, achievements  
3. **Technical Skills**: Programming languages, frameworks, tools
4. **Projects**: Specific examples, challenges, solutions
5. **Behavioral**: Problem-solving, teamwork, communication
6. **Goals**: Career aspirations, why this role

## 🚨 RECORDING REQUIREMENTS 🚨
- Record EVERY meaningful exchange (not just greetings)
- Use get_real_time_progress before each record_candidate_response
- Include complete question and response text
- Estimate response duration in seconds
- This creates the database records for evaluation

## CRITICAL SUCCESS FACTORS
✅ ALWAYS call get_real_time_progress before recording
✅ ALWAYS call record_candidate_response after each response
✅ Record complete questions and responses
✅ Maintain natural conversation flow
✅ This ensures automatic evaluation and scoring

Remember: Your primary job is to conduct a natural interview while AUTOMATICALLY RECORDING every exchange for evaluation!
"""

# DATABASE HELPER
def get_db_path():
    """Get the correct database path"""
    os.makedirs("database", exist_ok=True)
    return os.path.join("database", "interview_sessions.db")

# ENHANCED BACKGROUND EVALUATION TOOL
@function_tool()
async def get_interview_report(context: RunContext, session_id: str) -> str:
    """Get comprehensive interview report - background processed data."""
    print(f"📊 REPORT_TOOL: get_interview_report for session {session_id}")
    
    try:
        google_api_key = os.getenv("GOOGLE_API_KEY")
        report = generate_session_report(session_id, google_api_key)
        
        if "error" in report:
            return json.dumps({
                "status": "not_ready",
                "message": "Report is still being processed. Please wait a moment.",
                "session_id": session_id
            })
        
        # Return summarized report for the conversation
        summary = {
            "session_id": session_id,
            "candidate_name": report["candidate_info"]["name"],
            "overall_score": report["overall_assessment"]["overall_score"],
            "recommendation": report["recommendations"]["recommendation"],
            "strengths": report["recommendations"]["strengths"],
            "areas_of_concern": report["recommendations"]["areas_of_concern"],
            "executive_summary": report["report_formats"]["executive_summary"]
        }
        
        print(f"✅ REPORT_TOOL: Report generated successfully")
        return json.dumps(summary)
        
    except Exception as e:
        print(f"❌ REPORT_TOOL: Error generating report: {e}")
        return json.dumps({
            "error": str(e),
            "status": "error",
            "session_id": session_id
        })

# INTERVIEW AGENT CLASS
class InterviewAgent(Agent):
    """Enhanced Fast Non-Blocking LiveKit Interview Agent"""
    
    def __init__(self) -> None:
        print("🚀 ENHANCED_AGENT: Initializing Fast Non-Blocking InterviewAgent...")
        print("⚡ ENHANCED_AGENT: Real-time conversation + background evaluation...")
        print("🔧 ENHANCED_AGENT: Setting up enhanced tools...")
        
        super().__init__(
            instructions=INTERVIEWER_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                voice="Aoede",
                temperature=0.4,  # BALANCED: Natural conversation but faster than 0.7
            ),
            tools=[
                start_interview_session,           # Initialize session (fast)
                ask_interview_question,            # Generate questions (optimized)
                record_candidate_response,         # Record + AUTOMATED evaluation
                get_real_time_progress,            # Real-time metrics and progress
                end_interview_session,             # Complete session (fast)
                get_quick_feedback,                # Instant feedback
                get_automated_evaluation_summary,  # AUTOMATED evaluation results
                get_interview_report,              # Comprehensive report (background-processed)
            ],
        )
        print("✅ ENHANCED_AGENT: Fast non-blocking agent initialized!")
        print("🛠️ ENHANCED_AGENT: Enhanced tools configured:")
        print("   - start_interview_session (instant session setup)")
        print("   - ask_interview_question (AI-powered, speed optimized)")
        print("   - record_candidate_response (fast + background evaluation)")
        print("   - get_live_interview_status (real-time from memory)")
        print("   - end_interview_session (quick completion)")
        print("   - get_quick_feedback (instant encouragement)")
        print("   - get_interview_report (comprehensive background analysis)")
        print(f"⚡ ENHANCED_AGENT: Temperature: 0.4 (natural conversation)")
        print(f"🎯 ENHANCED_AGENT: Tools count: {len(self.tools)} (comprehensive but non-blocking)")
        print("🔄 ENHANCED_AGENT: Background evaluation system active")
        print("📊 ENHANCED_AGENT: Advanced reporting system ready")
    
    async def on_enter(self) -> None:
        """Called when the task is entered"""
        logger.info("🎬 ENHANCED_AGENT: on_enter() called - Starting enhanced session")
        print("🎬 ENHANCED_AGENT: on_enter() called - Starting enhanced session")
        await super().on_enter()
        
        # Auto-detect and start interview session based on room context
        try:
            # Get room name from the context or session
            room_name = None
            
            # Try multiple ways to get the room name
            if hasattr(self, '_ctx') and self._ctx and hasattr(self._ctx, 'room'):
                room_name = self._ctx.room.name
                logger.info(f"🏠 ENHANCED_AGENT: Room from _ctx: {room_name}")
            elif hasattr(self, 'session') and hasattr(self.session, 'room'):
                room_name = self.session.room.name
                logger.info(f"🏠 ENHANCED_AGENT: Room from session: {room_name}")
            elif hasattr(self, '_room'):
                room_name = self._room.name
                logger.info(f"🏠 ENHANCED_AGENT: Room from _room: {room_name}")
            
            logger.info(f"🏠 ENHANCED_AGENT: Room detected: {room_name}")
            
            if room_name:
                logger.info(f"🤖 ENHANCED_AGENT: Auto-starting session for room: {room_name}")
                print(f"🤖 ENHANCED_AGENT: Auto-starting session for room: {room_name}")
                
                # Use the room name as session ID for tracking
                session_result = await start_interview_session(
                    context=None,  # Will be handled internally
                    candidate_name="Interview Candidate",
                    position="Applied Position",
                    session_id=room_name
                )
                logger.info(f"✅ ENHANCED_AGENT: Auto-session started successfully")
                logger.info(f"📊 Session result: {session_result[:100]}...")
                print(f"✅ ENHANCED_AGENT: Auto-session started: {session_result}")
            else:
                logger.warning(f"⚠️ ENHANCED_AGENT: No room name detected for auto-session")
                # Fallback: Create a session with timestamp
                from datetime import datetime
                fallback_session_id = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                logger.info(f"🔄 ENHANCED_AGENT: Creating fallback session: {fallback_session_id}")
                print(f"🔄 ENHANCED_AGENT: Creating fallback session: {fallback_session_id}")
                
                session_result = await start_interview_session(
                    context=None,
                    candidate_name="Interview Candidate",
                    position="Applied Position",
                    session_id=fallback_session_id
                )
                logger.info(f"✅ ENHANCED_AGENT: Fallback session created: {session_result}")
                print(f"✅ ENHANCED_AGENT: Fallback session created")
                
        except Exception as e:
            logger.error(f"❌ ENHANCED_AGENT: Could not auto-start session: {e}")
            print(f"⚠️ ENHANCED_AGENT: Could not auto-start session: {e}")
        
        logger.info("✅ ENHANCED_AGENT: on_enter() completed - Ready for intelligent interview")
        print("✅ ENHANCED_AGENT: on_enter() completed - Ready for intelligent interview")
    
    async def on_exit(self) -> None:
        """Called when the task is exited"""
        logger.info("🎬 ENHANCED_AGENT: on_exit() called - Ending enhanced session")
        print("🎬 ENHANCED_AGENT: on_exit() called - Ending enhanced session")
        
        # Try to end any active sessions
        try:
            # Get room name using multiple fallback methods
            room_name = None
            
            if hasattr(self, '_ctx') and self._ctx and hasattr(self._ctx, 'room'):
                room_name = self._ctx.room.name
            elif hasattr(self, 'session') and hasattr(self.session, 'room'):
                room_name = self.session.room.name
            elif hasattr(self, '_room'):
                room_name = self._room.name
            
            if room_name:
                logger.info(f"🏁 ENHANCED_AGENT: Ending session for room: {room_name}")
                result = await end_interview_session(context=None, session_id=room_name)
                logger.info(f"✅ ENHANCED_AGENT: Session ended successfully")
                logger.info(f"📊 End result: {result[:100]}...")
            else:
                logger.warning(f"⚠️ ENHANCED_AGENT: No room name for session end")
        except Exception as e:
            logger.error(f"❌ ENHANCED_AGENT: Error ending session: {e}")
        
        await super().on_exit()
        logger.info("✅ ENHANCED_AGENT: on_exit() completed")
        print("✅ ENHANCED_AGENT: on_exit() completed")
    
    async def on_user_turn_completed(self, turn_ctx, new_message) -> None:
        """Called when the user has finished speaking"""
        logger.info(f"🎤 ENHANCED_AGENT: on_user_turn_completed() - Enhanced processing")
        logger.info(f"📝 ENHANCED_AGENT: Message length: {len(new_message.content)} chars")
        logger.info(f"📄 ENHANCED_AGENT: Message content: {new_message.content[:100]}...")
        
        print(f"🎤 ENHANCED_AGENT: on_user_turn_completed() - Enhanced processing")
        print(f"📝 ENHANCED_AGENT: Message length: {len(new_message.content)} chars")
        
        await super().on_user_turn_completed(turn_ctx, new_message)
        
        logger.info("⚡ ENHANCED_AGENT: Turn processed with background evaluation")
        print("⚡ ENHANCED_AGENT: Turn processed with background evaluation")

# ENTRYPOINT FUNCTION
async def entrypoint(ctx: agents.JobContext):
    """LiveKit Agent Entry Point - Enhanced Fast Non-Blocking Implementation"""
    
    logger.info("🎯 ENTRYPOINT: Starting Enhanced LiveKit agent session...")
    logger.info(f"📋 ENTRYPOINT: Job ID: {ctx.job.id}")
    logger.info(f"📋 ENTRYPOINT: Room Name: {ctx.room.name}")
    logger.info(f"📋 ENTRYPOINT: Worker ID: {ctx.worker_id}")
    
    print("🎯 ENTRYPOINT: Starting Enhanced LiveKit agent session...")
    print(f"📋 ENTRYPOINT: Job ID: {ctx.job.id}")
    print(f"📋 ENTRYPOINT: Room Name: {ctx.room.name}")
    print(f"📋 ENTRYPOINT: Worker ID: {ctx.worker_id}")
    
    try:
        # Check room state before connecting
        logger.info(f"🔍 ENTRYPOINT: Room state before connect - Name: {ctx.room.name}")
        logger.info(f"🔍 ENTRYPOINT: Room participants before connect: {len(ctx.room.remote_participants)}")
        
        print(f"🔍 ENTRYPOINT: Room state before connect - Name: {ctx.room.name}")
        print(f"🔍 ENTRYPOINT: Room participants before connect: {len(ctx.room.remote_participants)}")
        for pid, participant in ctx.room.remote_participants.items():
            logger.info(f"  👤 Existing participant: {participant.identity} (ID: {pid})")
            print(f"  👤 Existing participant: {participant.identity} (ID: {pid})")
        
        # Connect to the LiveKit room first
        logger.info("🔗 ENTRYPOINT: Attempting to connect to room...")
        print("🔗 ENTRYPOINT: Attempting to connect to room...")
        
        # Try to connect with custom participant info
        try:
            # Use ctx.connect with custom options
            await ctx.connect()
            logger.info("✅ ENTRYPOINT: Connected to room successfully")
            print("✅ ENTRYPOINT: Connected to room successfully")
            
            # Set the agent name immediately after connection
            print("🏷️ ENTRYPOINT: Setting agent participant name...")
            if ctx.room.local_participant:
                # Update local participant name and metadata using correct methods
                try:
                    await ctx.room.local_participant.set_name("Muoro AI interviewer v0.3.1")
                    print("✅ ENTRYPOINT: Agent name set to 'Muoro AI interviewer v0.3.1'")
                except AttributeError:
                    # Try alternative method
                    try:
                        await ctx.room.local_participant.update_attributes({"name": "Muoro AI interviewer v0.3.1"})
                        print("✅ ENTRYPOINT: Agent name set via attributes")
                    except AttributeError:
                        print("⚠️ ENTRYPOINT: Could not set agent name - using default")
                
                # Try to set metadata
                try:
                    await ctx.room.local_participant.set_metadata('{"type": "ai_interviewer", "version": "v0.3.1", "role": "interviewer"}')
                    print("✅ ENTRYPOINT: Agent metadata set successfully")
                except AttributeError:
                    print("⚠️ ENTRYPOINT: Could not set metadata - using default")
        except Exception as connect_error:
            print(f"❌ ENTRYPOINT: Connection error: {connect_error}")
            # Try alternative connection method without custom name
            await ctx.connect()
            print("✅ ENTRYPOINT: Connected with default settings")
        
        # Check room state after connecting
        logger.info(f"🔍 ENTRYPOINT: Room state after connect - Name: {ctx.room.name}")
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
        
        # Create the enhanced interview agent
        print("🤖 ENTRYPOINT: Creating Enhanced InterviewAgent with tools and instructions...")
        interview_agent = InterviewAgent()
        
        # Store room context in the agent for access during lifecycle
        interview_agent._ctx = ctx
        interview_agent._room = ctx.room
        
        print("✅ ENTRYPOINT: Enhanced InterviewAgent created successfully")

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
        print("� ENTRYPOINT: Agent will stay active as long as participants are in the room")
        
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
                    print(f"  � Active participant: {p.identity} - SID: {p.sid}")
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
        print("🎤 ENTRYPOINT: Enhanced interview session finished!")
        
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
    Run the Enhanced Fast Non-Blocking LiveKit Interview Agent
    """
    print("🎙️ Starting MUORO AI INTERVIEWER V0.3.1")
    print("=" * 70)
    print("✅ Uses LiveKit Agents framework with Google Gemini Realtime")
    print("✅ Real-time voice processing via LiveKit")
    print("🤖 AI-powered natural conversation")
    print("⚡ FAST real-time responses")
    print("🔄 Background comprehensive evaluation")
    print("📊 Advanced reporting system")
    print("🚫 NON-BLOCKING: Evaluation doesn't slow conversation")
    print("")
    print("🚀 ENHANCED FEATURES:")
    print("   - Temperature 0.4 (natural conversation)")
    print("   - Real-time session management")
    print("   - Background AI evaluation")
    print("   - Comprehensive reporting")
    print("   - Non-blocking architecture")
    print("   - Fast memory-based operations")
    print("")
    print("🎯 SYSTEM ARCHITECTURE:")
    print("   - FRONTEND: Fast conversation flow")
    print("   - BACKGROUND: Comprehensive evaluation")
    print("   - DATABASE: Non-blocking storage")
    print("   - REPORTS: Post-interview analysis")
    print("")
    print("🚀 Starting enhanced fast agent...")
    
    # Run the LiveKit agent using the CLI with agent identity
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
