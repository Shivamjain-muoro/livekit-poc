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

# Configure module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Ensure all handlers use the same format
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
for handler in logger.handlers:
    handler.setFormatter(formatter)

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
    logger.info("="*50)
    logger.info("🎯 QUESTION_GENERATION: Starting question generation process")
    logger.info(f"📝 Session ID: {session_id}")
    logger.info(f"🔄 Question Type: {question_type}")
    
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        logger.error("❌ QUESTION_GENERATION: Session not found")
        return json.dumps({"error": "Session not found"})
    
    try:
        # FULLY AI-GENERATED questions based on conversation context
        questions_asked = len(session.get("questions_asked", []))
        
        # Always use AI to generate contextual questions
        if os.getenv("GOOGLE_API_KEY"):
            if questions_asked == 0:
                # First question - but still AI generated based on role
                question = await _generate_opening_question(session)
            else:
                # All subsequent questions are AI-generated based on conversation
                logger.info("🤖 QUESTION_GENERATION: Using AI to generate adaptive technical question")
                question = await _generate_adaptive_technical_question(session)
                logger.info("✅ QUESTION_GENERATION: AI question generated successfully")
        else:
            # Fallback only if no API key (should rarely happen)
            logger.warning("⚠️ QUESTION_GENERATION: No Google API key found, using fallback questions")
            question = _get_fallback_question(questions_asked, session)
            logger.info("ℹ️ QUESTION_GENERATION: Using fallback question system")
        
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
            "status": "question_ready",
            "generation_method": "ai" if os.getenv("GOOGLE_API_KEY") else "fallback",
            "ai_enabled": bool(os.getenv("GOOGLE_API_KEY"))
        }
        
        logger.info("="*50)
        logger.info(f"✅ QUESTION_GENERATION: Question #{questions_asked + 1} generated")
        logger.info(f"🤖 Generation Method: {'AI (Gemini 1.5)' if os.getenv('GOOGLE_API_KEY') else 'Fallback System'}")
        logger.info(f"💭 Question: {question}")
        logger.info("="*50)
        
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

async def _generate_adaptive_technical_question(session):
    """Generate deep technical follow-up questions based on candidate responses"""
    try:
        logger.info("🤖 AI_QUESTION: Starting technical question generation...")
        logger.info(f"🎯 AI_QUESTION: Using Google Gemini 1.5 Flash model")
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Get all previous Q&A pairs
        questions_asked = session.get("questions_asked", [])
        responses_received = session.get("responses_received", [])
        question_count = len(questions_asked)
        
        logger.info(f"📊 AI_QUESTION: Context - {question_count} previous questions")
        logger.info(f"👤 AI_QUESTION: Role being interviewed: {session.get('position', 'Unknown')}")
        
        conversation_context = ""
        for i, q in enumerate(questions_asked):
            question_text = q["question"]
            if i < len(responses_received):
                response_text = responses_received[i].get("response", "")
                conversation_context += f"Q{i+1}: {question_text}\nA{i+1}: {response_text}\n\n"
        
        # Determine interview phase and focus
        if question_count == 1:
            focus_area = "technical experience and core skills"
            depth_level = "intermediate - build on their background"
        elif question_count <= 3:
            focus_area = "specific projects and implementations"  
            depth_level = "detailed - ask for concrete examples"
        elif question_count <= 6:
            focus_area = "advanced technical concepts, architecture, and problem-solving"
            depth_level = "deep - probe their technical decision-making"
        else:
            focus_area = "expert-level scenarios, leadership, and cutting-edge technologies"
            depth_level = "expert - challenge with complex scenarios"
        
        prompt = f"""You are conducting a technical interview for a {session['position']} position. 

INTERVIEW CONTEXT:
Question #{question_count + 1} - Focus: {focus_area}
Depth Level: {depth_level}

CONVERSATION SO FAR:
{conversation_context}

INSTRUCTIONS:
Based on their responses, generate 1 HIGHLY RELEVANT technical question that:

1. **BUILDS ON THEIR ANSWERS**: Reference specific technologies, projects, or concepts they mentioned
2. **INCREASES DEPTH**: Ask for implementation details, trade-offs, or technical decisions
3. **ASSESSES SKILL LEVEL**: Probe whether they truly understand what they're talking about
4. **STAYS CONVERSATIONAL**: Natural follow-up that feels like a real conversation

QUESTION TYPES TO USE:
- "You mentioned [X] - can you walk me through how you implemented [specific aspect]?"
- "That's interesting about [Y] - what challenges did you face and how did you solve them?"
- "When you used [technology], how did you handle [common challenge/consideration]?"
- "Can you give me a specific example of how you [technical task] in that project?"
- "What would you do differently if you had to [rebuild/optimize/scale] that solution?"

AVOID:
- Generic questions that ignore their responses
- Questions unrelated to what they've shared
- Yes/no questions
- Overly theoretical questions without practical context

Generate ONE specific, contextual technical question:"""
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.5,  # Slightly higher for more creative follow-ups
                max_output_tokens=200,
                top_p=0.9
            )
        )
        
        question = response.text.strip().strip('"').strip("'")
        
        # Enhanced fallback system based on interview phase
        if not question or len(question) < 10:
            if question_count == 1:
                question = "What programming languages and frameworks do you have the most experience with? I'd love to hear about specific projects where you've used them."
            elif question_count == 2:
                question = "Can you walk me through the architecture of a recent project you're proud of? What technologies did you choose and why?"
            elif question_count == 3:
                question = "Tell me about a challenging technical problem you've solved. What was your debugging and problem-solving approach?"
            else:
                technical_questions = [
                    "How do you approach code reviews and ensure code quality in your projects?",
                    "What's your experience with performance optimization and scaling applications?", 
                    "How do you handle database design and complex queries in your applications?",
                    "Tell me about your experience with API design and integration challenges.",
                    "What security considerations do you implement in your development process?",
                    "How do you approach testing - unit tests, integration tests, and quality assurance?",
                    "What's your experience with CI/CD and deployment strategies?",
                    "How do you stay current with new technologies and decide what to adopt?"
                ]
                question = technical_questions[(question_count - 4) % len(technical_questions)]
        
        return question
        
    except Exception as e:
        logger.error(f"Technical AI question generation error: {e}")
        # Fallback to context-appropriate questions
        if question_count == 1:
            return "What technologies are you most experienced with, and how have you used them in real projects?"
        elif question_count <= 3:
            return "Can you tell me about a specific project where you had to solve a complex technical challenge?"
        else:
            fallbacks = [
                "What design patterns or architectural principles do you find most useful?",
                "How do you approach troubleshooting and debugging in production environments?",
                "Tell me about your experience with version control and collaborative development.",
                "What's your process for learning new technologies and staying updated?",
                "How do you handle technical debt and maintain code quality over time?"
            ]
            return fallbacks[(question_count - 4) % len(fallbacks)]

async def _generate_opening_question(session):
    """Generate AI-powered opening question based on the position"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Generate a compelling opening question for a {session['position']} interview.

REQUIREMENTS:
- Should gather background, experience level, and key technologies
- Engaging and conversational tone
- Appropriate for voice interview
- Should help assess their skill level early
- Should be open-ended to let them showcase their strengths

EXAMPLES of good opening questions:
- "Tell me about your background and what got you excited about [technology stack] development?"
- "Walk me through your journey as a developer - what technologies have you worked with and what interests you most?"
- "I'd love to hear about your experience with [relevant tech] and what kind of projects you've built?"

Generate ONE opening question that fits the {session['position']} role:"""
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.4,
                max_output_tokens=100,
                top_p=0.9
            )
        )
        
        question = response.text.strip().strip('"').strip("'")
        
        # Fallback if AI fails
        if not question or len(question) < 10:
            question = f"Tell me about your background and what excites you most about working as a {session['position']}. What technologies have you been working with recently?"
        
        return question
        
    except Exception as e:
        logger.error(f"Opening question generation error: {e}")
        return f"Tell me about your background and experience. What technologies are you most passionate about working with in a {session['position']} role?"

def _get_fallback_question(questions_asked, session):
    """Fallback questions when AI is not available"""
    fallback_questions = [
        f"Tell me about your background and what interests you most about {session['position']} roles.",
        "What programming languages and frameworks do you have the most experience with?",
        "Can you walk me through a challenging project you've worked on recently?",
        "How do you approach problem-solving when debugging complex issues?",
        "Tell me about your experience with database design and optimization.",
        "How do you handle scaling and performance challenges in applications?",
        "What security considerations do you keep in mind when developing?",
        "How do you approach testing and quality assurance in your development process?",
        "Tell me about your experience with deployment and CI/CD processes.",
        "What's a recent technology you've learned and how are you applying it?"
    ]
    
    return fallback_questions[min(questions_asked, len(fallback_questions) - 1)]

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
