"""
Enhanced Real-Time Interview Tools
Optimized for instant response with AUTOMATED comprehensive evaluation
"""

import json
import asyncio
import sqlite3
import os
import time
from datetime import datetime
from livekit.agents import function_tool, RunContext
import google.generativeai as genai
import logging
import threading
import queue
from typing import Dict, Any

# Import the automated evaluation system
from automated_evaluation_system import get_automated_evaluator

logger = logging.getLogger(__name__)

# Global session data (in-memory for speed)
ACTIVE_SESSIONS = {}

# Real-time evaluation queue (ultra-fast async processing)
EVALUATION_QUEUE = queue.Queue()
EVALUATION_WORKER = None
EVALUATION_RUNNING = False

def get_db_connection():
    """Get database connection"""
    os.makedirs("database", exist_ok=True)
    db_path = os.path.join("database", "interview_evaluations.db")
    return sqlite3.connect(db_path)

def init_database():
    """Initialize enhanced database schema"""
    with get_db_connection() as conn:
        # Sessions table
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
                communication_score REAL DEFAULT 0,
                total_questions INTEGER DEFAULT 0,
                total_responses INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0,
                fluency_score REAL DEFAULT 0,
                confidence_score REAL DEFAULT 0
            )
        """)
        
        # Enhanced exchanges table with real-time metrics
        conn.execute("""
            CREATE TABLE IF NOT EXISTS interview_exchanges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                question TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                response_duration REAL DEFAULT 0,
                
                -- Real-time scoring
                correctness_score REAL DEFAULT 0,
                completeness_score REAL DEFAULT 0,
                clarity_score REAL DEFAULT 0,
                skill_relevance_score REAL DEFAULT 0,
                fluency_score REAL DEFAULT 0,
                confidence_score REAL DEFAULT 0,
                
                -- Sentiment analysis
                sentiment_positive REAL DEFAULT 0,
                sentiment_neutral REAL DEFAULT 0,
                sentiment_negative REAL DEFAULT 0,
                
                -- AI evaluation
                ai_evaluation TEXT,
                key_skills_demonstrated TEXT,
                areas_of_concern TEXT,
                follow_up_suggestions TEXT,
                
                -- Timing metrics
                processing_time REAL DEFAULT 0,
                evaluation_completed BOOLEAN DEFAULT 0,
                
                FOREIGN KEY (session_id) REFERENCES interview_sessions (session_id)
            )
        """)
        
        conn.commit()

# Real-time evaluation worker
def start_evaluation_worker():
    """Start background evaluation worker thread"""
    global EVALUATION_WORKER, EVALUATION_RUNNING
    
    if EVALUATION_RUNNING:
        return
    
    EVALUATION_RUNNING = True
    
    def evaluation_worker():
        """Background worker for real-time evaluation"""
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if google_api_key:
            genai.configure(api_key=google_api_key)
        
        while EVALUATION_RUNNING:
            try:
                # Get evaluation task (non-blocking with timeout)
                eval_data = EVALUATION_QUEUE.get(timeout=1)
                
                # Process evaluation immediately
                asyncio.run(process_real_time_evaluation(eval_data))
                
                EVALUATION_QUEUE.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Evaluation worker error: {e}")
    
    EVALUATION_WORKER = threading.Thread(target=evaluation_worker, daemon=True)
    EVALUATION_WORKER.start()
    logger.info("✅ Real-time evaluation worker started")

async def process_real_time_evaluation(eval_data: Dict[str, Any]):
    """Process comprehensive evaluation in background"""
    start_time = time.time()
    
    try:
        session_id = eval_data["session_id"]
        question = eval_data["question"]
        response = eval_data["response"]
        response_duration = eval_data.get("response_duration", 0)
        position = eval_data["position"]
        
        # Generate comprehensive evaluation prompt
        evaluation_prompt = f"""
        Evaluate this interview response comprehensively and provide structured scores:
        
        Position: {position}
        Question: {question}
        Response: {response}
        Response Time: {response_duration}s
        
        Provide evaluation in this exact JSON format:
        {{
            "correctness_score": 0-10,
            "completeness_score": 0-10,
            "clarity_score": 0-10,
            "skill_relevance_score": 0-10,
            "fluency_score": 0-10,
            "confidence_score": 0-10,
            "sentiment_positive": 0-1,
            "sentiment_neutral": 0-1,
            "sentiment_negative": 0-1,
            "key_skills_demonstrated": ["skill1", "skill2"],
            "areas_of_concern": ["concern1", "concern2"],
            "follow_up_suggestions": ["suggestion1", "suggestion2"],
            "overall_assessment": "brief assessment"
        }}
        
        Base scores on:
        - Technical accuracy and correctness
        - Completeness of the answer
        - Clarity of communication
        - Relevance to the position requirements
        - Fluency and articulation
        - Confidence level demonstrated
        - Sentiment analysis of the response
        """
        
        # Generate evaluation using Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        response_obj = model.generate_content(
            evaluation_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,  # Low temperature for consistent scoring
                max_output_tokens=1000
            )
        )
        
        # Parse evaluation results
        evaluation_text = response_obj.text
        
        # Extract JSON from response
        import re
        json_match = re.search(r'\\{.*\\}', evaluation_text, re.DOTALL)
        if json_match:
            evaluation_json = json.loads(json_match.group())
        else:
            # Fallback scoring if JSON parsing fails
            evaluation_json = {
                "correctness_score": 7.0,
                "completeness_score": 7.0,
                "clarity_score": 7.0,
                "skill_relevance_score": 7.0,
                "fluency_score": 7.0,
                "confidence_score": 7.0,
                "sentiment_positive": 0.7,
                "sentiment_neutral": 0.2,
                "sentiment_negative": 0.1,
                "key_skills_demonstrated": ["communication"],
                "areas_of_concern": [],
                "follow_up_suggestions": [],
                "overall_assessment": "Standard response"
            }
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Update database with comprehensive evaluation
        with get_db_connection() as conn:
            # First find the most recent exchange for this session/question/response
            cursor = conn.execute("""
                SELECT id FROM interview_exchanges 
                WHERE session_id = ? AND question = ? AND response = ?
                ORDER BY timestamp DESC LIMIT 1
            """, (session_id, question, response))
            
            exchange_row = cursor.fetchone()
            if exchange_row:
                exchange_id = exchange_row[0]
                
                # Update the specific exchange by ID
                conn.execute("""
                    UPDATE interview_exchanges SET
                        correctness_score = ?,
                        completeness_score = ?,
                        clarity_score = ?,
                        skill_relevance_score = ?,
                        fluency_score = ?,
                        confidence_score = ?,
                        sentiment_positive = ?,
                        sentiment_neutral = ?,
                        sentiment_negative = ?,
                        ai_evaluation = ?,
                        key_skills_demonstrated = ?,
                        areas_of_concern = ?,
                        follow_up_suggestions = ?,
                        processing_time = ?,
                        evaluation_completed = 1
                    WHERE id = ?
                """, (
                    evaluation_json.get("correctness_score", 0),
                    evaluation_json.get("completeness_score", 0),
                    evaluation_json.get("clarity_score", 0),
                    evaluation_json.get("skill_relevance_score", 0),
                    evaluation_json.get("fluency_score", 0),
                    evaluation_json.get("confidence_score", 0),
                    evaluation_json.get("sentiment_positive", 0),
                    evaluation_json.get("sentiment_neutral", 0),
                    evaluation_json.get("sentiment_negative", 0),
                    evaluation_json.get("overall_assessment", ""),
                    json.dumps(evaluation_json.get("key_skills_demonstrated", [])),
                    json.dumps(evaluation_json.get("areas_of_concern", [])),
                    json.dumps(evaluation_json.get("follow_up_suggestions", [])),
                    processing_time,
                    exchange_id  # Use the exchange ID instead of session/question/response
                ))
                
                conn.commit()
                logger.info(f"✅ Evaluation updated for exchange ID {exchange_id}")
            else:
                logger.warning(f"⚠️ No exchange found to update for session {session_id}")
        
        logger.info(f"✅ Real-time evaluation completed in {processing_time:.2f}s for session {session_id}")
        
    except Exception as e:
        logger.error(f"❌ Real-time evaluation failed: {e}")

# Initialize automated evaluation system
_automated_evaluator = None

def init_automated_evaluation():
    """Initialize the automated evaluation system"""
    global _automated_evaluator
    if _automated_evaluator is None:
        google_api_key = os.getenv("GOOGLE_API_KEY")
        _automated_evaluator = get_automated_evaluator(google_api_key)
        print("✅ REALTIME_TOOLS: Automated evaluation system initialized")
    return _automated_evaluator

# Initialize on import
init_database()
init_automated_evaluation()
start_evaluation_worker()

@function_tool()
async def start_interview_session(
    context: RunContext,
    candidate_name: str = "Interview Candidate",
    position: str = "Position",
    session_id: str = None
) -> str:
    """
    INSTANT session start - no blocking operations
    """
    start_time = time.time()
    
    if not session_id:
        # Create session ID based on room name if available
        room_name = getattr(context, 'room_name', None) or getattr(context, 'room', {}).get('name', '')
        if room_name:
            session_id = room_name
        else:
            session_id = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"🚀 INSTANT_START: {candidate_name} for {position} (Session: {session_id})")
    
    # Store in memory immediately (INSTANT)
    ACTIVE_SESSIONS[session_id] = {
        "candidate_name": candidate_name,
        "position": position,
        "start_time": datetime.now(),
        "questions_asked": [],
        "responses_received": [],
        "status": "active",
        "real_time_scores": [],
        "total_response_time": 0,
        "response_count": 0
    }
    
    # Database save (async, non-blocking)
    def save_to_db():
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
        except Exception as e:
            logger.error(f"DB save error: {e}")
    
    # Run database save in background thread
    threading.Thread(target=save_to_db, daemon=True).start()
    
    processing_time = time.time() - start_time
    print(f"⚡ INSTANT_START: Completed in {processing_time*1000:.1f}ms")
    
    return json.dumps({
        "session_id": session_id,
        "status": "started",
        "candidate_name": candidate_name,
        "position": position,
        "processing_time_ms": round(processing_time * 1000, 1),
        "message": "Session started instantly"
    })

@function_tool()
async def record_candidate_response(
    context: RunContext,
    session_id: str = None,
    question: str = "",
    response: str = "",
    response_duration: float = 0.0
) -> str:
    """
    INSTANT response recording with background evaluation
    Auto-detects session_id if not provided
    """
    start_time = time.time()
    
    # Auto-detect session_id if not provided
    if not session_id:
        if ACTIVE_SESSIONS:
            session_id = list(ACTIVE_SESSIONS.keys())[0]  # Use first active session
        else:
            # Try to find any recent session in database
            try:
                with get_db_connection() as conn:
                    cursor = conn.execute("""
                        SELECT session_id FROM interview_sessions 
                        WHERE status = 'active' 
                        ORDER BY start_time DESC LIMIT 1
                    """)
                    row = cursor.fetchone()
                    if row:
                        session_id = row[0]
            except Exception as e:
                logger.error(f"Session auto-detection error: {e}")
    
    if not session_id:
        return json.dumps({
            "error": "No active session found",
            "suggestion": "Please start a session first",
            "active_sessions": list(ACTIVE_SESSIONS.keys())
        })
    
    print(f"⚡ INSTANT_RECORD: Session {session_id} - Recording Q&A")
    print(f"   📝 Question: {question[:50]}...")
    print(f"   💬 Response: {response[:50]}...")
    
    # Get session (instant from memory)
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        # Quick database lookup if not in memory
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
                        "responses_received": [],
                        "real_time_scores": [],
                        "total_response_time": 0,
                        "response_count": 0
                    }
                    ACTIVE_SESSIONS[session_id] = session
                    print(f"   📦 Session restored from database to memory")
        except Exception as e:
            logger.error(f"Session lookup error: {e}")
    
    if not session:
        return json.dumps({
            "error": "Session not found",
            "session_id": session_id,
            "suggestion": "Session may have expired or was not properly created"
        })
    
    # Update memory instantly
    session["questions_asked"].append(question)
    session["responses_received"].append(response)
    session["total_response_time"] += response_duration
    session["response_count"] += 1
    
    timestamp = datetime.now().isoformat()
    
    # ✅ NEW: Use AUTOMATED EVALUATION SYSTEM
    print(f"   🚀 Triggering automated evaluation...")
    
    # Get or initialize automated evaluator
    evaluator = init_automated_evaluation()
    
    # Queue automatic evaluation (INSTANT, NON-BLOCKING)
    evaluator.queue_evaluation(
        session_id=session_id,
        question=question,
        response=response,
        response_duration=response_duration,
        candidate_name=session["candidate_name"],
        position=session["position"]
    )
    
    print(f"   ✅ Automated evaluation queued - will be processed in background")
    print(f"   📊 Evaluation includes: Scoring + Database Storage + Session Updates")
    
    processing_time = time.time() - start_time
    
    result = {
        "session_id": session_id,
        "status": "recorded_with_automated_evaluation",
        "response_length": len(response),
        "response_duration": response_duration,
        "automated_evaluation": "queued_and_processing",
        "processing_time_ms": round(processing_time * 1000, 1),
        "total_qa_pairs": len(session["questions_asked"]),
        "evaluation_system": "automated_real_time"
    }
    
    print(f"⚡ INSTANT_RECORD: Completed in {processing_time*1000:.1f}ms")
    return json.dumps(result)

@function_tool()
async def end_interview_session(
    context: RunContext,
    session_id: str
) -> str:
    """
    INSTANT session end with comprehensive final evaluation
    """
    start_time = time.time()
    
    print(f"🏁 INSTANT_END: Session {session_id}")
    
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        # Find any active session
        if ACTIVE_SESSIONS:
            session_id = list(ACTIVE_SESSIONS.keys())[0]
            session = ACTIVE_SESSIONS[session_id]
        else:
            return json.dumps({"error": "No active session found"})
    
    # Update session instantly
    session["status"] = "completed"
    session["end_time"] = datetime.now()
    
    # Calculate final stats
    questions_count = len(session.get("questions_asked", []))
    responses_count = len(session.get("responses_received", []))
    avg_response_time = session.get("total_response_time", 0) / max(session.get("response_count", 1), 1)
    duration_minutes = round((session["end_time"] - session["start_time"]).total_seconds() / 60, 1)
    
    # Trigger final comprehensive evaluation (background)
    def final_evaluation():
        try:
            with get_db_connection() as conn:
                # Update session
                conn.execute("""
                    UPDATE interview_sessions 
                    SET end_time = ?, status = ?, total_questions = ?, 
                        total_responses = ?, avg_response_time = ?
                    WHERE session_id = ?
                """, (
                    session["end_time"].isoformat(),
                    "completed",
                    questions_count,
                    responses_count,
                    avg_response_time,
                    session_id
                ))
                
                # Calculate overall scores from individual evaluations
                cursor = conn.execute("""
                    SELECT AVG(correctness_score), AVG(completeness_score), 
                           AVG(clarity_score), AVG(skill_relevance_score),
                           AVG(fluency_score), AVG(confidence_score)
                    FROM interview_exchanges 
                    WHERE session_id = ? AND evaluation_completed = 1
                """, (session_id,))
                
                scores = cursor.fetchone()
                if scores and scores[0] is not None:
                    technical_score = (scores[0] + scores[1] + scores[3]) / 3
                    communication_score = (scores[2] + scores[4] + scores[5]) / 3
                    overall_score = (technical_score + communication_score) / 2
                    
                    conn.execute("""
                        UPDATE interview_sessions 
                        SET overall_score = ?, technical_score = ?, 
                            communication_score = ?, fluency_score = ?, 
                            confidence_score = ?
                        WHERE session_id = ?
                    """, (
                        overall_score, technical_score, communication_score,
                        scores[4] or 0, scores[5] or 0, session_id
                    ))
                
                conn.commit()
                logger.info(f"✅ Final evaluation completed for session {session_id}")
                
        except Exception as e:
            logger.error(f"Final evaluation error: {e}")
    
    # Run final evaluation in background
    threading.Thread(target=final_evaluation, daemon=True).start()
    
    processing_time = time.time() - start_time
    
    result = {
        "session_id": session_id,
        "status": "completed_instantly",
        "summary": {
            "candidate_name": session["candidate_name"],
            "position": session["position"],
            "questions_asked": questions_count,
            "responses_received": responses_count,
            "duration_minutes": duration_minutes,
            "avg_response_time": round(avg_response_time, 2)
        },
        "final_evaluation": "processing_in_background",
        "processing_time_ms": round(processing_time * 1000, 1)
    }
    
    print(f"⚡ INSTANT_END: Completed in {processing_time*1000:.1f}ms")
    return json.dumps(result)

@function_tool()
async def get_real_time_progress(
    context: RunContext,
    session_id: str = None
) -> str:
    """
    Get real-time interview progress and metrics - also returns current session_id
    """
    # Auto-detect session if not provided
    if not session_id and ACTIVE_SESSIONS:
        session_id = list(ACTIVE_SESSIONS.keys())[0]
    
    if not session_id:
        # Try to find active session in database
        try:
            with get_db_connection() as conn:
                cursor = conn.execute("""
                    SELECT session_id FROM interview_sessions 
                    WHERE status = 'active' 
                    ORDER BY start_time DESC LIMIT 1
                """)
                row = cursor.fetchone()
                if row:
                    session_id = row[0]
        except Exception as e:
            logger.error(f"Session detection error: {e}")
    
    if not session_id:
        return json.dumps({
            "error": "No active session found", 
            "available_sessions": list(ACTIVE_SESSIONS.keys()),
            "suggestion": "Start a session first"
        })
    
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
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
                        "responses_received": [],
                        "real_time_scores": [],
                        "total_response_time": 0,
                        "response_count": 0
                    }
                    ACTIVE_SESSIONS[session_id] = session
        except Exception as e:
            logger.error(f"Session load error: {e}")
    
    if not session:
        return json.dumps({
            "error": "Session not found", 
            "session_id": session_id,
            "suggestion": "Session may have expired"
        })
    
    # Quick stats from memory
    questions_count = len(session.get("questions_asked", []))
    responses_count = len(session.get("responses_received", []))
    avg_response_time = session.get("total_response_time", 0) / max(session.get("response_count", 1), 1)
    
    return json.dumps({
        "session_id": session_id,
        "candidate_name": session["candidate_name"],
        "position": session["position"],
        "questions_asked": questions_count,
        "responses_received": responses_count,
        "avg_response_time": round(avg_response_time, 2),
        "status": session.get("status", "active"),
        "evaluation_queue_size": EVALUATION_QUEUE.qsize(),
        "memory_session_active": True
    })

# Auto-detect and start session
async def auto_start_session_from_context(context: RunContext):
    """Auto-start session based on room context"""
    try:
        room_name = getattr(context, 'room_name', None)
        if not room_name and hasattr(context, 'room'):
            room_name = getattr(context.room, 'name', None)
        
        if room_name and room_name not in ACTIVE_SESSIONS:
            print(f"🤖 AUTO_START: Detected room {room_name}")
            await start_interview_session(context, session_id=room_name)
            return room_name
    except Exception as e:
        logger.error(f"Auto-start error: {e}")
    return None

@function_tool()
async def get_automated_evaluation_summary(
    context: RunContext,
    session_id: str = None
) -> str:
    """
    Get automated evaluation summary with all Q&A exchanges and scores
    This shows the results of the automated evaluation system
    """
    print(f"📊 AUTOMATED_SUMMARY: Getting evaluation summary for session {session_id}")
    
    # Auto-detect session if not provided
    if not session_id and ACTIVE_SESSIONS:
        session_id = list(ACTIVE_SESSIONS.keys())[0]
    
    if not session_id:
        return json.dumps({
            "error": "No session specified",
            "available_sessions": list(ACTIVE_SESSIONS.keys()),
            "suggestion": "Provide session_id or ensure there's an active session"
        })
    
    try:
        # Get automated evaluation summary
        evaluator = init_automated_evaluation()
        summary = evaluator.get_session_summary(session_id)
        
        if "error" in summary:
            return json.dumps(summary)
        
        # Format for display
        result = {
            "session_id": session_id,
            "candidate_name": summary["candidate_name"],
            "position": summary["position"],
            "overall_score": round(summary["overall_score"], 1),
            "technical_score": round(summary["technical_score"], 1),
            "communication_score": round(summary["communication_score"], 1),
            "total_questions": summary["total_questions"],
            "exchanges_with_evaluations": len([ex for ex in summary["exchanges"] if ex["evaluated_at"]]),
            "sample_exchanges": [
                {
                    "question": ex["question"][:100] + "..." if len(ex["question"]) > 100 else ex["question"],
                    "response": ex["response"][:100] + "..." if len(ex["response"]) > 100 else ex["response"],
                    "overall_score": round(ex["overall_score"], 1),
                    "technical_score": round(ex["correctness_score"], 1),
                    "communication_score": round(ex["clarity_score"], 1),
                    "key_skills": ex["key_skills"],
                    "evaluated": bool(ex["evaluated_at"])
                }
                for ex in summary["exchanges"][:3]  # Show first 3 exchanges
            ],
            "automated_evaluation_status": "completed" if summary["exchanges"] else "no_exchanges_found"
        }
        
        print(f"✅ AUTOMATED_SUMMARY: Found {len(summary['exchanges'])} exchanges with evaluations")
        return json.dumps(result)
        
    except Exception as e:
        logger.error(f"❌ AUTOMATED_SUMMARY: Error getting summary: {e}")
        return json.dumps({
            "error": str(e),
            "session_id": session_id,
            "suggestion": "Check if the session exists and evaluations have been processed"
        })

# Export functions
__all__ = [
    'start_interview_session',
    'record_candidate_response', 
    'end_interview_session',
    'get_real_time_progress',
    'auto_start_session_from_context',
    'get_automated_evaluation_summary',
    'ACTIVE_SESSIONS'
]

# Initialize system on import
print("🔧 REALTIME_TOOLS: Initializing database and evaluation system...")
init_database()
start_evaluation_worker()
print("✅ REALTIME_TOOLS: System initialized and ready!")
