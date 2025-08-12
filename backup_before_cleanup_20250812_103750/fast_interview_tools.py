"""
Fast Non-Blocking Interview Tools
Real-time tools that queue background processing
"""

import json
import asyncio
from datetime import datetime
from livekit.agents import function_tool, RunContext
from background_evaluator import queue_interview_data, get_background_evaluator
import google.generativeai as genai
import os
import logging

logger = logging.getLogger(__name__)

# Global session data (in-memory for speed)
ACTIVE_SESSIONS = {}

@function_tool()
async def start_interview_session(
    context: RunContext,
    candidate_name: str,
    position: str,
    session_id: str = None
) -> str:
    """
    Initialize a new interview session - FAST execution with background setup
    """
    if not session_id:
        session_id = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"🚀 FAST_TOOL: start_interview_session - {candidate_name} for {position}")
    
    # Store session data in memory for fast access
    ACTIVE_SESSIONS[session_id] = {
        "candidate_name": candidate_name,
        "position": position,
        "start_time": datetime.now(),
        "questions_asked": [],
        "responses_received": [],
        "current_question_index": 0,
        "status": "active"
    }
    
    # Quick response to keep conversation flowing
    result = {
        "session_id": session_id,
        "status": "started",
        "candidate_name": candidate_name,
        "position": position,
        "message": f"Interview session started for {candidate_name}. Ready to begin!"
    }
    
    print(f"✅ FAST_TOOL: Session {session_id} started (no blocking operations)")
    return json.dumps(result)

@function_tool()
async def ask_interview_question(
    context: RunContext,
    session_id: str,
    question_type: str = "adaptive"
) -> str:
    """
    Generate and ask next interview question - OPTIMIZED for speed
    """
    print(f"🎯 FAST_TOOL: ask_interview_question - Session: {session_id}")
    
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        return json.dumps({"error": "Session not found"})
    
    try:
        # FAST question generation based on conversation flow
        questions_asked = len(session.get("questions_asked", []))
        
        if questions_asked == 0:
            # Opening question - pre-defined for speed
            question = f"Tell me about your background and what interests you most about {session['position']} roles."
        elif questions_asked == 1:
            # Follow-up - adaptive but fast
            question = "Can you walk me through a challenging project you've worked on recently?"
        elif questions_asked == 2:
            # Technical question
            question = f"What technical skills do you think are most important for a {session['position']}?"
        elif questions_asked == 3:
            # Behavioral question
            question = "How do you handle working under tight deadlines or pressure?"
        else:
            # Use AI for deeper questions, but with speed optimization
            if os.getenv("GOOGLE_API_KEY"):
                question = await _generate_adaptive_question(session)
            else:
                question = "What questions do you have about this role or our team?"
        
        # Store question in session (fast memory operation)
        session["questions_asked"].append({
            "question": question,
            "timestamp": datetime.now(),
            "type": question_type
        })
        session["current_question_index"] = questions_asked
        
        result = {
            "question": question,
            "question_number": questions_asked + 1,
            "session_id": session_id,
            "status": "question_ready"
        }
        
        print(f"✅ FAST_TOOL: Generated question #{questions_asked + 1} quickly")
        return json.dumps(result)
        
    except Exception as e:
        print(f"❌ FAST_TOOL: Error generating question: {e}")
        return json.dumps({
            "question": "Tell me more about your experience.",
            "error": str(e),
            "session_id": session_id
        })

async def _generate_adaptive_question(session):
    """Generate adaptive question using AI (optimized for speed)"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        previous_questions = [q["question"] for q in session["questions_asked"]]
        
        prompt = f"""Generate 1 great follow-up interview question for {session['position']}.

Previous questions asked:
{json.dumps(previous_questions)}

Requirements:
- Build on previous conversation
- Engaging and conversational
- Appropriate for voice interview
- One question only

Just return the question, no extra text."""
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=100,  # Very limited for speed
                top_p=0.9
            )
        )
        
        question = response.text.strip().strip('"').strip("'")
        return question
        
    except Exception as e:
        logger.error(f"AI question generation error: {e}")
        return "What other aspects of your experience would you like to highlight?"

@function_tool()
async def record_candidate_response(
    context: RunContext,
    session_id: str,
    candidate_response: str,
    response_duration: float = 0.0
) -> str:
    """
    Record candidate response - FAST storage with background evaluation
    """
    print(f"📝 FAST_TOOL: record_candidate_response - Session: {session_id}")
    print(f"📊 FAST_TOOL: Response length: {len(candidate_response)} chars")
    
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        return json.dumps({"error": "Session not found"})
    
    try:
        # Get current question
        current_question_idx = session.get("current_question_index", 0)
        questions_asked = session.get("questions_asked", [])
        
        if current_question_idx < len(questions_asked):
            current_question = questions_asked[current_question_idx]["question"]
        else:
            current_question = "Previous question"
        
        # FAST in-memory storage
        response_data = {
            "response": candidate_response,
            "timestamp": datetime.now(),
            "duration": response_duration,
            "question": current_question
        }
        
        session["responses_received"].append(response_data)
        
        # QUEUE FOR BACKGROUND PROCESSING (non-blocking)
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if google_api_key:
            queue_interview_data(
                session_id=session_id,
                candidate_name=session["candidate_name"],
                position=session["position"],
                question=current_question,
                response=candidate_response,
                google_api_key=google_api_key
            )
            print(f"📥 FAST_TOOL: Queued for background evaluation")
        
        # Quick response quality assessment (no AI, just basic metrics)
        quick_quality = "good"
        if len(candidate_response) > 200:
            quick_quality = "detailed"
        elif len(candidate_response) < 30:
            quick_quality = "brief"
        
        result = {
            "status": "recorded",
            "session_id": session_id,
            "response_quality": quick_quality,
            "response_length": len(candidate_response),
            "evaluation_status": "queued_for_background_processing",
            "message": "Response recorded successfully"
        }
        
        print(f"✅ FAST_TOOL: Response recorded and queued for evaluation")
        return json.dumps(result)
        
    except Exception as e:
        print(f"❌ FAST_TOOL: Error recording response: {e}")
        return json.dumps({
            "error": str(e),
            "status": "error",
            "session_id": session_id
        })

@function_tool()
async def get_live_interview_status(
    context: RunContext,
    session_id: str
) -> str:
    """
    Get current interview status - INSTANT response from memory
    """
    print(f"📊 FAST_TOOL: get_live_interview_status - Session: {session_id}")
    
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        return json.dumps({"error": "Session not found"})
    
    # Calculate basic stats from memory (instant)
    questions_count = len(session.get("questions_asked", []))
    responses_count = len(session.get("responses_received", []))
    
    # Calculate interview progress
    progress_percentage = min((questions_count / 8) * 100, 100)  # Assume 8 questions max
    
    status = {
        "session_id": session_id,
        "candidate_name": session["candidate_name"],
        "position": session["position"],
        "questions_asked": questions_count,
        "responses_received": responses_count,
        "progress_percentage": round(progress_percentage, 1),
        "status": session["status"],
        "duration_minutes": round((datetime.now() - session["start_time"]).total_seconds() / 60, 1),
        "next_action": "ask_question" if questions_count == responses_count else "wait_for_response"
    }
    
    print(f"✅ FAST_TOOL: Status retrieved instantly from memory")
    return json.dumps(status)

@function_tool()
async def end_interview_session(
    context: RunContext,
    session_id: str
) -> str:
    """
    End interview session - FAST completion with background report generation
    """
    print(f"🏁 FAST_TOOL: end_interview_session - Session: {session_id}")
    
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        return json.dumps({"error": "Session not found"})
    
    # Update session status
    session["status"] = "completed"
    session["end_time"] = datetime.now()
    
    # Basic summary from memory (instant)
    questions_count = len(session.get("questions_asked", []))
    responses_count = len(session.get("responses_received", []))
    duration_minutes = round((session["end_time"] - session["start_time"]).total_seconds() / 60, 1)
    
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
        "message": f"Interview completed! Detailed evaluation will be available shortly.",
        "report_available_in": "1-2 minutes"
    }
    
    print(f"✅ FAST_TOOL: Session ended, background processing continues")
    return json.dumps(result)

@function_tool()
async def get_quick_feedback(
    context: RunContext,
    session_id: str
) -> str:
    """
    Get quick feedback during interview - NON-BLOCKING
    """
    print(f"💬 FAST_TOOL: get_quick_feedback - Session: {session_id}")
    
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        return json.dumps({"error": "Session not found"})
    
    # Quick assessment from memory data
    responses = session.get("responses_received", [])
    
    if not responses:
        feedback = "Great start! Keep the conversation flowing naturally."
    else:
        last_response = responses[-1]
        response_length = len(last_response["response"])
        
        if response_length > 150:
            feedback = "Excellent detailed response! You're providing great insights."
        elif response_length < 50:
            feedback = "Good answer! Feel free to elaborate more on your experience."
        else:
            feedback = "Perfect! Your responses are clear and well-structured."
    
    result = {
        "session_id": session_id,
        "quick_feedback": feedback,
        "encouragement": "You're doing great! Keep being yourself.",
        "status": "ongoing"
    }
    
    print(f"✅ FAST_TOOL: Quick feedback provided instantly")
    return json.dumps(result)
