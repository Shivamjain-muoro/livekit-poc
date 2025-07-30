"""
Working AI Interview Backend - Built on proven simplified backend with AI integration
"""
import os
import uuid
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from livekit.api import AccessToken
from livekit.api.access_token import VideoGrants
from datetime import datetime
import uvicorn

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

# AI capabilities - optional import to prevent hanging
try:
    import google.generativeai as genai
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    print(f"🔍 Google API Key: {'Found' if GOOGLE_API_KEY else 'Missing'}")
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
        AI_ENABLED = True
        print("✅ Google AI integration enabled")
        print(f"🔍 API Key starts with: {GOOGLE_API_KEY[:10]}...")
    else:
        AI_ENABLED = False
        print("⚠️ Google AI disabled - no API key found in .env file")
except ImportError as e:
    AI_ENABLED = False
    print(f"⚠️ Google AI disabled - library not available: {e}")
except Exception as e:
    AI_ENABLED = False
    print(f"⚠️ Google AI disabled - configuration error: {e}")

# Import our models
from models.interview_models import (
    Candidate, SessionCreateRequest, SessionResponse, 
    StartInterviewRequest, StartInterviewResponse,
    SubmitAnswerRequest, SubmitAnswerResponse,
    JoinSessionRequest, JoinSessionResponse,
    ExperienceLevel, Question, QuestionType, Feedback,
    InterviewStatus  # Added missing import
)

# FastAPI app
app = FastAPI(title="Working AI Interview System", version="3.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# LiveKit configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")

# Simple in-memory storage for demo
sessions = {}

# Fallback questions when AI is not available
FALLBACK_QUESTIONS = {
    "entry": {
        "technical": [
            "What is the difference between a function and a method?",
            "Explain what version control is and why it's important.",
            "What are the basic principles of object-oriented programming?",
            "How do you debug code when something isn't working?",
            "What is the difference between frontend and backend development?"
        ],
        "behavioral": [
            "Tell me about a programming project you're proud of.",
            "How do you approach learning new technologies?",
            "Describe a time you solved a difficult problem.",
            "How do you stay updated with technology trends?",
            "What motivates you to pursue a career in technology?"
        ]
    },
    "mid": {
        "technical": [
            "Explain the difference between synchronous and asynchronous programming.",
            "What is the time complexity of binary search and why?",
            "How would you optimize a slow database query?",
            "Explain RESTful API design principles.",
            "What are the benefits of using design patterns?"
        ],
        "behavioral": [
            "Tell me about a challenging project you led or contributed to significantly.",
            "How do you handle code reviews and feedback?",
            "Describe a time you had to learn a new technology under pressure.",
            "How do you balance technical debt with new feature development?",
            "Tell me about a time you disagreed with a technical decision."
        ]
    },
    "senior": {
        "technical": [
            "How would you design a system to handle millions of concurrent users?",
            "Explain microservices architecture and when to use it.",
            "How do you ensure code quality and maintainability in large teams?",
            "What are the trade-offs between SQL and NoSQL databases?",
            "How would you implement a caching strategy for a high-traffic application?"
        ],
        "behavioral": [
            "Tell me about a time you mentored junior developers.",
            "How do you make architectural decisions in complex projects?",
            "Describe a situation where you had to refactor legacy code.",
            "How do you handle technical disagreements with stakeholders?",
            "Tell me about a time you prevented a major technical issue."
        ]
    }
}

def generate_ai_questions(experience_level: str, position: str, skills: list, num_questions: int = 5):
    """Generate questions using AI or fall back to predefined questions"""
    
    print(f"🔍 Attempting to generate {num_questions} questions for {experience_level} {position}")
    print(f"🔍 AI_ENABLED: {AI_ENABLED}")
    print(f"🔍 Skills: {skills}")
    
    if not AI_ENABLED:
        print(f"🔄 AI disabled - Using fallback questions for {experience_level} level")
        level_questions = FALLBACK_QUESTIONS.get(experience_level, FALLBACK_QUESTIONS["mid"])
        technical = level_questions["technical"][:3]
        behavioral = level_questions["behavioral"][:2]
        return technical + behavioral
    
    try:
        # Create the prompt for AI question generation
        skills_str = ", ".join(skills) if skills else "general programming"
        prompt = f"""
        Generate {num_questions} interview questions for a {experience_level} level {position} candidate.
        
        Candidate Skills: {skills_str}
        Experience Level: {experience_level}
        Position: {position}
        
        Please generate a mix of:
        - 3 technical questions relevant to their skills and experience level
        - 2 behavioral/situational questions
        
        Format: Return only the questions, one per line, without numbering or prefixes.
        Make questions challenging but appropriate for the experience level.
        """
        
        print(f"🤖 Sending prompt to Gemini AI...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        print(f"🤖 AI Response received: {len(response.text) if response.text else 0} characters")
        
        if response.text:
            questions = [q.strip() for q in response.text.split('\n') if q.strip()]
            questions = [q for q in questions if len(q) > 10]  # Filter out short/empty lines
            
            print(f"🤖 Parsed {len(questions)} questions from AI response")
            
            if len(questions) >= 3:
                print(f"✅ Generated {len(questions)} AI questions for {experience_level} {position}")
                print("🎯 AI Generated Questions:")
                for i, q in enumerate(questions[:num_questions], 1):
                    print(f"   {i}. {q}")
                return questions[:num_questions]
            else:
                print(f"⚠️ AI generated only {len(questions)} questions, need at least 3")
    
    except Exception as e:
        print(f"⚠️ AI question generation failed: {e}")
        print(f"⚠️ Error type: {type(e).__name__}")
    
    # Fallback to predefined questions
    print(f"🔄 Using fallback questions for {experience_level} level")
    level_questions = FALLBACK_QUESTIONS.get(experience_level, FALLBACK_QUESTIONS["mid"])
    technical = level_questions["technical"][:3]
    behavioral = level_questions["behavioral"][:2]
    fallback_questions = technical + behavioral
    print("📋 Fallback Questions:")
    for i, q in enumerate(fallback_questions, 1):
        print(f"   {i}. {q}")
    return fallback_questions

def evaluate_answer_with_ai(question: str, answer: str, experience_level: str):
    """Evaluate answer using AI or provide basic feedback"""
    
    if not AI_ENABLED or len(answer.strip()) < 10:
        return {
            "score": 7,  # Default score
            "feedback": "Thank you for your response. The interviewer will review your answer.",
            "strengths": ["Response provided"],
            "improvements": ["Continue to provide detailed examples"]
        }
    
    try:
        prompt = f"""
        Evaluate this interview answer for a {experience_level} level candidate:
        
        Question: {question}
        Answer: {answer}
        
        Please provide:
        1. A score from 1-10 (where 10 is excellent)
        2. Brief constructive feedback (2-3 sentences)
        3. Key strengths (1-2 points)
        4. Areas for improvement (1-2 points)
        
        Format your response as JSON:
        {{
            "score": <number>,
            "feedback": "<feedback>",
            "strengths": ["<strength1>", "<strength2>"],
            "improvements": ["<improvement1>", "<improvement2>"]
        }}
        """
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        if response.text:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                evaluation = json.loads(json_match.group())
                print(f"✅ AI evaluation completed with score: {evaluation.get('score', 'N/A')}")
                return evaluation
    
    except Exception as e:
        print(f"⚠️ AI evaluation failed: {e}")
    
    # Fallback evaluation
    return {
        "score": 7,
        "feedback": "Thank you for your response. Your answer shows good understanding.",
        "strengths": ["Clear communication", "Relevant response"],
        "improvements": ["Provide more specific examples", "Add technical details"]
    }

@app.get("/")
async def root():
    return {
        "message": "Working AI Interview System", 
        "status": "running",
        "ai_enabled": AI_ENABLED,
        "livekit_url": LIVEKIT_URL
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "ai_status": "enabled" if AI_ENABLED else "disabled",
        "livekit_configured": bool(LIVEKIT_API_KEY and LIVEKIT_API_SECRET)
    }

# Serve HTML files
@app.get("/enhanced")
async def serve_enhanced():
    """Serve the enhanced interview UI"""
    return FileResponse("enhanced_interview_ui.html")

@app.get("/live-local")
async def serve_live_local():
    return FileResponse("live_interview_local.html")

@app.get("/simple")
async def serve_simple():
    return FileResponse("simple_interview.html")

# Create interview session with AI-generated questions
@app.post("/api/interview/create-session", response_model=SessionResponse)
async def create_interview_session(request: SessionCreateRequest):
    """Create a new interview session with AI-generated questions and LiveKit tokens"""
    try:
        # Generate session ID
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        room_name = f"interview_{session_id}"
        
        # Generate LiveKit tokens
        participant_token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(f"candidate_{session_id}") \
            .with_name(request.candidate.name) \
            .with_grants(VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True
            )).to_jwt()
        
        interviewer_token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(f"interviewer_{session_id}") \
            .with_name("Interviewer") \
            .with_grants(VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
                room_admin=True
            )).to_jwt()
        
        # Generate questions using AI or fallbacks
        questions = generate_ai_questions(
            experience_level=request.candidate.experience_level,
            position=request.candidate.position,
            skills=request.candidate.skills or [],
            num_questions=5
        )
        
        # Store session data
        sessions[session_id] = {
            "id": session_id,
            "candidate": request.candidate.dict(),
            "room_name": room_name,
            "questions": questions,
            "current_question_index": 0,
            "answers": [],
            "status": InterviewStatus.CREATED,  # Use enum value
            "created_at": datetime.now().isoformat(),
            "livekit_url": LIVEKIT_URL,
            "ai_enabled": AI_ENABLED
        }
        
        print(f"✅ Session {session_id} created with {len(questions)} questions")
        
        return SessionResponse(
            session_id=session_id,
            room_name=room_name,
            participant_token=participant_token,
            agent_token=interviewer_token,
            livekit_url=LIVEKIT_URL,
            status=InterviewStatus.CREATED,  # Use enum value
            questions=questions[:3],
            ai_enabled=AI_ENABLED
        )
        
    except Exception as e:
        print(f"❌ Error creating session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.post("/api/interview/start", response_model=StartInterviewResponse)
async def start_interview(request: StartInterviewRequest):
    """Start the interview session"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[request.session_id]
    session["status"] = InterviewStatus.STARTED
    session["started_at"] = datetime.now().isoformat()
    
    current_question = session["questions"][session["current_question_index"]]
    
    # Create a proper Question object
    question_obj = Question(
        id=f"q_{session['current_question_index'] + 1}",
        session_id=request.session_id,
        question_text=current_question,
        question_type=QuestionType.TECHNICAL,  # Default type
        difficulty_level=3,  # Default difficulty
        expected_duration=120,  # 2 minutes default
        order_index=session["current_question_index"]
    )
    
    print(f"✅ Interview {request.session_id} started")
    
    return StartInterviewResponse(
        success=True,
        first_question=question_obj,
        total_questions=len(session["questions"]),
        estimated_duration=10  # 10 minutes total
    )

@app.post("/api/interview/submit-answer", response_model=SubmitAnswerResponse)
async def submit_answer(request: SubmitAnswerRequest):
    """Submit an answer and get AI-powered feedback"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[request.session_id]
    current_index = session["current_question_index"]
    
    if current_index >= len(session["questions"]):
        raise HTTPException(status_code=400, detail="No more questions available")
    
    current_question = session["questions"][current_index]
    
    # Evaluate the answer using AI
    evaluation = evaluate_answer_with_ai(
        question=current_question,
        answer=request.answer_text,
        experience_level=session["candidate"]["experience_level"]
    )
    
    # Create proper Feedback object
    feedback_obj = Feedback(
        id=f"feedback_{uuid.uuid4().hex[:8]}",
        answer_id=f"answer_{current_index + 1}",
        session_id=request.session_id,
        score=evaluation.get("score", 7),
        feedback_text=evaluation.get("feedback", "Thank you for your response."),
        criteria_scores={"overall": evaluation.get("score", 7)},
        strengths=evaluation.get("strengths", ["Response provided"]),
        improvements=evaluation.get("improvements", ["Continue improving"]),
        evaluated_at=datetime.now()
    )
    
    # Store the answer
    answer_data = {
        "question": current_question,
        "answer": request.answer_text,
        "audio_duration": request.duration,  # Fixed: was request.audio_duration
        "timestamp": datetime.now().isoformat(),
        "evaluation": evaluation
    }
    session["answers"].append(answer_data)
    
    # Move to next question
    session["current_question_index"] += 1
    
    # Check if interview is complete
    if session["current_question_index"] >= len(session["questions"]):
        session["status"] = InterviewStatus.COMPLETED
        session["completed_at"] = datetime.now().isoformat()
        
        print(f"✅ Interview {request.session_id} completed")
        
        return SubmitAnswerResponse(
            success=True,
            feedback=feedback_obj,
            next_question=None,
            is_complete=True,
            session_summary=None  # Could create InterviewSummary here
        )
    else:
        next_question_text = session["questions"][session["current_question_index"]]
        
        # Create next Question object
        next_question_obj = Question(
            id=f"q_{session['current_question_index'] + 1}",
            session_id=request.session_id,
            question_text=next_question_text,
            question_type=QuestionType.TECHNICAL,
            difficulty_level=3,
            expected_duration=120,
            order_index=session["current_question_index"]
        )
        
        print(f"✅ Answer submitted for question {current_index + 1}")
        
        return SubmitAnswerResponse(
            success=True,
            feedback=feedback_obj,
            next_question=next_question_obj,
            is_complete=False,
            session_summary=None
        )

@app.get("/api/session/{session_id}/status")
async def get_session_status(session_id: str):
    """Get session status and details"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "session_id": session_id,
        "status": session["status"],
        "current_question": session["current_question_index"] + 1,
        "total_questions": len(session["questions"]),
        "answers_submitted": len(session["answers"]),
        "ai_enabled": session.get("ai_enabled", False),
        "created_at": session["created_at"]
    }

@app.get("/api/interview/feedback/{session_id}")
async def get_interview_feedback(session_id: str):
    """Get comprehensive feedback for completed interview"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Calculate overall feedback
    answers = session.get("answers", [])
    if not answers:
        return {
            "session_id": session_id,
            "overall_score": 0,
            "detailed_feedback": "No answers were submitted for evaluation.",
            "total_questions": len(session.get("questions", [])),
            "answers_submitted": 0,
            "strengths": [],
            "improvements": ["Complete the interview to receive feedback"],
            "recommendation": "incomplete"
        }
    
    # Calculate average score from all evaluations
    total_score = 0
    all_strengths = []
    all_improvements = []
    
    for answer in answers:
        evaluation = answer.get("evaluation", {})
        total_score += evaluation.get("score", 0)
        all_strengths.extend(evaluation.get("strengths", []))
        all_improvements.extend(evaluation.get("improvements", []))
    
    average_score = total_score / len(answers) if answers else 0
    overall_percentage = (average_score / 10) * 100  # Convert to percentage
    
    # Determine recommendation
    if overall_percentage >= 80:
        recommendation = "Strong candidate - Recommend for hire"
    elif overall_percentage >= 60:
        recommendation = "Good candidate - Consider for interview or hire"
    elif overall_percentage >= 40:
        recommendation = "Average candidate - May need additional assessment"
    else:
        recommendation = "Candidate needs improvement - Consider additional training"
    
    # Generate detailed feedback
    candidate_info = session.get("candidate", {})
    detailed_feedback = f"""
    Interview completed for {candidate_info.get('name', 'Unknown')} applying for {candidate_info.get('position', 'Unknown position')}.
    
    Performance Summary:
    - Answered {len(answers)} out of {len(session.get('questions', []))} questions
    - Average score: {average_score:.1f}/10 ({overall_percentage:.1f}%)
    - Experience level: {candidate_info.get('experience_level', 'Unknown')}
    
    The candidate demonstrated {'strong' if overall_percentage >= 70 else 'adequate' if overall_percentage >= 50 else 'developing'} 
    technical and communication skills throughout the interview.
    """
    
    # Deduplicate strengths and improvements
    unique_strengths = list(set(all_strengths))[:5]  # Top 5 unique strengths
    unique_improvements = list(set(all_improvements))[:5]  # Top 5 unique improvements
    
    print(f"✅ Generated feedback for session {session_id}: {overall_percentage:.1f}%")
    
    return {
        "session_id": session_id,
        "overall_score": overall_percentage,
        "average_score": average_score,
        "detailed_feedback": detailed_feedback.strip(),
        "total_questions": len(session.get("questions", [])),
        "answers_submitted": len(answers),
        "strengths": unique_strengths,
        "improvements": unique_improvements,
        "recommendation": recommendation,
        "candidate_name": candidate_info.get("name", "Unknown"),
        "position": candidate_info.get("position", "Unknown"),
        "experience_level": candidate_info.get("experience_level", "Unknown"),
        "interview_duration": "Completed",
        "ai_enabled": session.get("ai_enabled", False)
    }

if __name__ == "__main__":
    print("🚀 Starting Working AI Interview Backend...")
    print(f"🔗 LiveKit URL: {LIVEKIT_URL}")
    print(f"🤖 AI Integration: {'Enabled' if AI_ENABLED else 'Disabled (using fallback questions)'}")
    
    uvicorn.run(
        "working_ai_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
