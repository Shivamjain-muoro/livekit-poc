"""
Fixed Interview Tools with Database Integration
Tools that properly save interview data to database
"""

import json
import asyncio
import sqlite3
import os
from datetime import datetime
from livekit.agents import function_tool, RunContext
from background_evaluator import queue_interview_data, get_background_evaluator
import google.generativeai as genai
import logging

# Configure detailed logging
import logging
import os

# Remove any existing handlers to prevent conflicts
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure fresh logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('interview_detailed.log', encoding='utf-8'),
        logging.StreamHandler()
    ],
    force=True
)

logger = logging.getLogger('InterviewTools')

# Global session data (in-memory for speed)
ACTIVE_SESSIONS = {}

def get_db_connection():
    """Get database connection"""
    os.makedirs("database", exist_ok=True)
    db_path = os.path.join("database", "interview_evaluations.db")
    return sqlite3.connect(db_path)

def init_database():
    """Initialize database schema"""
    with get_db_connection() as conn:
        # Create sessions table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS interview_sessions (
                session_id TEXT PRIMARY KEY,
                candidate_name TEXT NOT NULL,
                position TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                status TEXT DEFAULT 'active',
                overall_score REAL DEFAULT 0,
                technical_score REAL DEFAULT 0,
                communication_score REAL DEFAULT 0
            )
        """)
        
        # Create exchanges table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS interview_exchanges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                question TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                response_duration REAL,
                relevance_score REAL DEFAULT 0,
                clarity_score REAL DEFAULT 0,
                depth_score REAL DEFAULT 0,
                ai_evaluation TEXT,
                key_points TEXT,
                concerns TEXT,
                FOREIGN KEY (session_id) REFERENCES interview_sessions (session_id)
            )
        """)
        
        conn.commit()

# Initialize database on import
init_database()

@function_tool()
async def start_interview_session(
    context: RunContext,
    candidate_name: str = "Interview Candidate",
    position: str = "Position",
    session_id: str = None
) -> str:
    """
    Initialize a new interview session with database storage
    """
    logger.info(f"🚀 STARTING INTERVIEW SESSION")
    logger.info(f"   📋 Candidate: {candidate_name}")
    logger.info(f"   💼 Position: {position}")
    logger.info(f"   🆔 Requested Session ID: {session_id}")
    
    if not session_id:
        # Create session ID based on room name if available
        room_name = getattr(context, 'room_name', None) or getattr(context, 'room', {}).get('name', '')
        if room_name:
            session_id = room_name
            logger.info(f"   🏠 Using room name as session ID: {room_name}")
        else:
            session_id = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"   🆔 Generated new session ID: {session_id}")
    
    logger.info(f"🚀 DATABASE_TOOL: start_interview_session - {candidate_name} for {position}")
    logger.info(f"🆔 Final Session ID: {session_id}")
    
    # Store session data in memory for fast access
    session_data = {
        "candidate_name": candidate_name,
        "position": position,
        "start_time": datetime.now(),
        "questions_asked": [],
        "responses_received": [],
        "current_question_index": 0,
        "status": "active"
    }
    
    ACTIVE_SESSIONS[session_id] = session_data
    logger.info(f"✅ Session stored in memory with {len(session_data)} fields")
    
    # Save to database immediately
    try:
        with get_db_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO interview_sessions 
                (session_id, candidate_name, position, start_time, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                candidate_name,
                position,
                datetime.now().isoformat(),
                "active"
            ))
            conn.commit()
        logger.info(f"✅ DATABASE_TOOL: Session saved to database successfully")
        print(f"✅ DATABASE_TOOL: Session saved to database")
    except Exception as e:
        logger.error(f"❌ DATABASE_TOOL: Error saving session: {e}")
        print(f"❌ DATABASE_TOOL: Error saving session: {e}")
    
    # Queue for background evaluation setup (session start doesn't need Q&A data)
    # We'll queue data when actual Q&A exchanges happen
    logger.info(f"📝 Session start completed - ready for Q&A exchanges")
    
    result = {
        "session_id": session_id,
        "status": "started",
        "candidate_name": candidate_name,
        "position": position,
        "message": f"Interview session started for {candidate_name}",
        "database_saved": True
    }
    
    logger.info(f"✅ DATABASE_TOOL: Session initialized with database storage")
    logger.info(f"📊 Session result: {result}")
    print(f"✅ DATABASE_TOOL: Session initialized with database storage")
    return json.dumps(result)

@function_tool()
async def record_candidate_response(
    context: RunContext,
    session_id: str,
    question: str,
    response: str,
    response_duration: float = 0.0
) -> str:
    """
    Record candidate response with immediate database storage
    """
    logger.info(f"📝 RECORDING CANDIDATE RESPONSE")
    logger.info(f"   🆔 Session ID: {session_id}")
    logger.info(f"   ❓ Question: {question[:100]}{'...' if len(question) > 100 else ''}")
    logger.info(f"   💬 Response: {response[:100]}{'...' if len(response) > 100 else ''}")
    logger.info(f"   ⏱️ Response Duration: {response_duration}s")
    
    print(f"📝 DATABASE_TOOL: record_candidate_response - Session: {session_id}")
    
    # Get session from memory or database
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        logger.warning(f"⚠️ Session {session_id} not found in memory, checking database")
        # Try to load from database
        try:
            with get_db_connection() as conn:
                cursor = conn.execute("""
                    SELECT candidate_name, position, start_time, status
                    FROM interview_sessions WHERE session_id = ?
                """, (session_id,))
                row = cursor.fetchone()
                if row:
                    session = {
                        "candidate_name": row[0],
                        "position": row[1],
                        "start_time": datetime.fromisoformat(row[2]),
                        "status": row[3],
                        "questions_asked": [],
                        "responses_received": []
                    }
                    ACTIVE_SESSIONS[session_id] = session
                    logger.info(f"✅ Session loaded from database: {row[0]} for {row[1]}")
        except Exception as e:
            logger.error(f"❌ DATABASE_TOOL: Could not load session: {e}")
            print(f"❌ DATABASE_TOOL: Could not load session: {e}")
    
    if not session:
        logger.error(f"❌ Session {session_id} not found in memory or database")
        print(f"❌ DATABASE_TOOL: Session {session_id} not found")
        return json.dumps({"error": "Session not found"})
    
    # Add to memory
    session["questions_asked"].append(question)
    session["responses_received"].append(response)
    logger.info(f"✅ Added to memory - Total Q&A pairs: {len(session['questions_asked'])}")
    
    timestamp = datetime.now().isoformat()
    logger.info(f"🕐 Timestamp: {timestamp}")
    
    # Save to database immediately
    try:
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO interview_exchanges 
                (session_id, question, response, timestamp, response_duration)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                question,
                response,
                timestamp,
                response_duration
            ))
            conn.commit()
        logger.info(f"✅ DATABASE_TOOL: Exchange saved to database successfully")
        print(f"✅ DATABASE_TOOL: Exchange saved to database")
    except Exception as e:
        logger.error(f"❌ DATABASE_TOOL: Error saving exchange: {e}")
        print(f"❌ DATABASE_TOOL: Error saving exchange: {e}")
    
    # Queue for background evaluation
    logger.info(f"🔄 Queuing background evaluation...")
    try:
        queue_interview_data(
            session_id=session_id,
            candidate_name=session["candidate_name"],
            position=session["position"],
            question=question,
            response=response,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        logger.info(f"✅ Background evaluation queued successfully")
    except Exception as e:
        logger.error(f"❌ Background evaluation queue failed: {e}")
    
    result = {
        "session_id": session_id,
        "status": "recorded",
        "question": question[:100] + "..." if len(question) > 100 else question,
        "response_length": len(response),
        "background_evaluation": "queued",
        "database_saved": True
    }
    
    logger.info(f"✅ DATABASE_TOOL: Response recorded and queued for evaluation")
    logger.info(f"📊 Response result: {result}")
    print(f"✅ DATABASE_TOOL: Response recorded and queued for evaluation")
    return json.dumps(result)

@function_tool()
async def end_interview_session(
    context: RunContext,
    session_id: str
) -> str:
    """
    End interview session with database update
    """
    logger.info(f"🏁 ENDING INTERVIEW SESSION")
    logger.info(f"   🆔 Requested Session ID: {session_id}")
    
    print(f"🏁 DATABASE_TOOL: end_interview_session - Session: {session_id}")
    
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        logger.warning(f"⚠️ Session {session_id} not found in memory")
        # Try to find any active session if specific ID not found
        if ACTIVE_SESSIONS:
            session_id = list(ACTIVE_SESSIONS.keys())[0]
            session = ACTIVE_SESSIONS[session_id]
            logger.info(f"🔄 Using found active session: {session_id}")
            print(f"🔄 DATABASE_TOOL: Using found session: {session_id}")
        else:
            logger.error(f"❌ No active sessions found")
            print(f"❌ DATABASE_TOOL: No active sessions found")
            return json.dumps({"error": "No active session found"})
    
    # Log session details before ending
    logger.info(f"📊 SESSION SUMMARY BEFORE END:")
    logger.info(f"   👤 Candidate: {session.get('candidate_name', 'Unknown')}")
    logger.info(f"   💼 Position: {session.get('position', 'Unknown')}")
    logger.info(f"   ❓ Questions Asked: {len(session.get('questions_asked', []))}")
    logger.info(f"   💬 Responses Received: {len(session.get('responses_received', []))}")
    logger.info(f"   🕐 Start Time: {session.get('start_time', 'Unknown')}")
    
    # Update session status
    session["status"] = "completed"
    session["end_time"] = datetime.now()
    logger.info(f"   🕐 End Time: {session['end_time']}")
    
    # Update database
    try:
        with get_db_connection() as conn:
            conn.execute("""
                UPDATE interview_sessions 
                SET end_time = ?, status = ?
                WHERE session_id = ?
            """, (
                session["end_time"].isoformat(),
                "completed",
                session_id
            ))
            conn.commit()
        logger.info(f"✅ DATABASE_TOOL: Session status updated to 'completed' in database")
        print(f"✅ DATABASE_TOOL: Session completed in database")
    except Exception as e:
        logger.error(f"❌ DATABASE_TOOL: Error updating session: {e}")
        print(f"❌ DATABASE_TOOL: Error updating session: {e}")
    
    # Calculate basic stats
    questions_count = len(session.get("questions_asked", []))
    responses_count = len(session.get("responses_received", []))
    duration_minutes = round((session["end_time"] - session["start_time"]).total_seconds() / 60, 1)
    
    logger.info(f"📈 FINAL STATISTICS:")
    logger.info(f"   ❓ Total Questions: {questions_count}")
    logger.info(f"   💬 Total Responses: {responses_count}")
    logger.info(f"   ⏱️ Duration: {duration_minutes} minutes")
    
    # Queue final evaluation (if there were any Q&A exchanges)
    if questions_count > 0 and responses_count > 0:
        logger.info(f"🔄 Queuing final evaluation for {questions_count} Q&A pairs")
        # Get last Q&A for final evaluation
        try:
            with get_db_connection() as conn:
                cursor = conn.execute("""
                    SELECT question, response FROM interview_exchanges 
                    WHERE session_id = ? 
                    ORDER BY timestamp DESC LIMIT 1
                """, (session_id,))
                last_qa = cursor.fetchone()
                
                if last_qa:
                    logger.info(f"📝 Final Q&A for evaluation: Q={last_qa[0][:50]}... A={last_qa[1][:50]}...")
                    queue_interview_data(
                        session_id=session_id,
                        candidate_name=session["candidate_name"],
                        position=session["position"],
                        question=last_qa[0],
                        response=last_qa[1],
                        google_api_key=os.getenv("GOOGLE_API_KEY")
                    )
                    logger.info(f"✅ Final evaluation queued successfully")
                else:
                    logger.warning(f"⚠️ No Q&A exchanges found for final evaluation")
        except Exception as e:
            logger.error(f"⚠️ DATABASE_TOOL: Could not queue final evaluation: {e}")
            print(f"⚠️ DATABASE_TOOL: Could not queue final evaluation: {e}")
    else:
        logger.warning(f"⚠️ No Q&A exchanges to evaluate (Q:{questions_count}, R:{responses_count})")
    
    result = {
        "session_id": session_id,
        "status": "completed",
        "summary": {
            "candidate_name": session["candidate_name"],
            "position": session["position"],
            "questions_asked": questions_count,
            "responses_received": responses_count,
            "duration_minutes": duration_minutes
        },
        "evaluation_status": "processing_in_background",
        "message": f"Interview completed! Data saved to database.",
        "database_saved": True
    }
    
    logger.info(f"✅ DATABASE_TOOL: Session ended and saved to database")
    logger.info(f"📊 Final result: {result}")
    print(f"✅ DATABASE_TOOL: Session ended and saved to database")
    return json.dumps(result)

@function_tool()
async def get_live_interview_status(
    context: RunContext,
    session_id: str = None
) -> str:
    """
    Get current interview status from database
    """
    print(f"📊 DATABASE_TOOL: get_live_interview_status")
    
    if not session_id and ACTIVE_SESSIONS:
        session_id = list(ACTIVE_SESSIONS.keys())[0]
    
    if not session_id:
        return json.dumps({"error": "No session specified or active"})
    
    try:
        with get_db_connection() as conn:
            # Get session info
            cursor = conn.execute("""
                SELECT candidate_name, position, start_time, status
                FROM interview_sessions WHERE session_id = ?
            """, (session_id,))
            session_row = cursor.fetchone()
            
            if not session_row:
                return json.dumps({"error": "Session not found in database"})
            
            # Get exchange count
            cursor = conn.execute("""
                SELECT COUNT(*) FROM interview_exchanges WHERE session_id = ?
            """, (session_id,))
            exchange_count = cursor.fetchone()[0]
            
            result = {
                "session_id": session_id,
                "candidate_name": session_row[0],
                "position": session_row[1],
                "start_time": session_row[2],
                "status": session_row[3],
                "exchanges_count": exchange_count,
                "database_connected": True
            }
            
            print(f"✅ DATABASE_TOOL: Status retrieved from database")
            return json.dumps(result)
            
    except Exception as e:
        print(f"❌ DATABASE_TOOL: Error getting status: {e}")
        return json.dumps({"error": str(e)})

# Auto-detect and start session based on room context
async def auto_start_session_from_context(context: RunContext):
    """Auto-start session based on room context"""
    logger.info(f"🤖 AUTO_START: Attempting to auto-detect and start session")
    try:
        room_name = getattr(context, 'room_name', None)
        logger.info(f"🏠 Room name from context.room_name: {room_name}")
        
        if not room_name and hasattr(context, 'room'):
            room_name = getattr(context.room, 'name', None)
            logger.info(f"🏠 Room name from context.room.name: {room_name}")
        
        if room_name:
            logger.info(f"🔍 Checking if session already exists for room: {room_name}")
            if room_name not in ACTIVE_SESSIONS:
                logger.info(f"🚀 AUTO_START: Starting new session for room {room_name}")
                print(f"🤖 AUTO_START: Detected room {room_name}, starting session")
                result = await start_interview_session(context, session_id=room_name)
                logger.info(f"✅ AUTO_START: Session started successfully for room {room_name}")
                logger.info(f"📊 AUTO_START result: {result[:100]}...")
                return room_name
            else:
                logger.info(f"ℹ️ Session already exists for room {room_name}")
                return room_name
        else:
            logger.warning(f"⚠️ AUTO_START: No room name found in context")
            return None
    except Exception as e:
        logger.error(f"❌ AUTO_START: Error: {e}")
        print(f"❌ AUTO_START: Error: {e}")
    return None

# Export functions for the main agent
__all__ = [
    'start_interview_session',
    'record_candidate_response', 
    'end_interview_session',
    'get_live_interview_status',
    'auto_start_session_from_context',
    'ACTIVE_SESSIONS'
]
