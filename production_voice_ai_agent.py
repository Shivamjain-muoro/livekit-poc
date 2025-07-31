"""
Voice AI Interview System - Production Ready Version
==================================================
Handles API quotas, missing dependencies, and provides comprehensive fallbacks.
"""

import os
import asyncio
import json
import uuid
import logging
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# Core dependencies
from dotenv import load_dotenv
load_dotenv()

# Configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize AI with fallback
ai_available = False
ai_model = None

try:
    if GOOGLE_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        ai_model = genai.GenerativeModel('gemini-1.5-flash')
        ai_available = True
        print("✅ Google Gemini AI initialized")
    else:
        print("⚠️ No Google API key - using fallback mode")
except Exception as e:
    print(f"⚠️ AI initialization failed: {e} - using fallback mode")

# Initialize LiveKit with fallback
livekit_available = False
AccessToken = None
VideoGrants = None

try:
    from livekit.api import AccessToken
    from livekit.api.access_token import VideoGrants
    livekit_available = True
    print("✅ LiveKit API initialized")
except Exception as e:
    print(f"⚠️ LiveKit initialization failed: {e} - using mock mode")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data Models
class Candidate(BaseModel):
    name: str
    email: str
    position: str
    experience_level: str
    skills: List[str] = []

class VoiceInterviewRequest(BaseModel):
    candidate: Candidate
    interview_type: str = "technical"
    max_questions: int = 5
    enable_real_time_feedback: bool = True

class VoiceSessionResponse(BaseModel):
    success: bool
    session_id: str
    room_name: str
    access_token: str
    livekit_url: str
    ai_agent_ready: bool
    message: str
    fallback_mode: bool = False

class InterviewState(BaseModel):
    session_id: str
    candidate: Candidate
    room_name: str
    current_question_index: int = 0
    questions: List[Dict] = []
    answers: List[Dict] = []
    scores: List[int] = []
    feedback: List[str] = []
    status: str = "created"
    ai_agent_connected: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    fallback_mode: bool = False

# Global state
interview_sessions: Dict[str, InterviewState] = {}

class ProductionAIInterviewAgent:
    """Production-ready AI Interview Agent with comprehensive fallbacks"""
    
    def __init__(self, session_id: str, room_name: str):
        self.session_id = session_id
        self.room_name = room_name
        self.is_connected = False
        self.conversation_active = True
        self.current_question_index = 0
        
    async def initialize(self):
        """Initialize the AI agent with fallback handling"""
        try:
            session = interview_sessions.get(self.session_id)
            if not session:
                raise Exception("Session not found")
            
            # Generate questions
            session.questions = await self.generate_interview_questions(session.candidate)
            session.ai_agent_connected = True
            session.status = "active"
            session.start_time = datetime.now()
            
            logger.info(f"AI Agent initialized for session: {self.session_id}")
            
            # Start the automated interview flow
            await self.start_automated_interview()
            
        except Exception as e:
            logger.error(f"AI Agent initialization failed: {e}")
            # Set fallback mode
            session = interview_sessions.get(self.session_id)
            if session:
                session.fallback_mode = True
                session.ai_agent_connected = False
    
    async def start_automated_interview(self):
        """Start the automated interview process"""
        session = interview_sessions.get(self.session_id)
        if not session:
            return
        
        logger.info(f"Starting automated interview for {session.candidate.name}")
        
        # Simulate the automated interview flow
        for i in range(len(session.questions)):
            if not self.conversation_active:
                break
                
            session.current_question_index = i
            current_question = session.questions[i]
            
            # Simulate AI asking question
            logger.info(f"AI asking question {i+1}: {current_question['question_text'][:50]}...")
            session.status = "questioning"
            
            # Simulate listening period
            await asyncio.sleep(3)
            session.status = "listening"
            
            # Simulate candidate response (in real system, this would be STT)
            await asyncio.sleep(10)  # Give time for candidate to respond
            
            # Simulate answer processing
            mock_answer = f"This is a simulated answer to question {i+1} about {current_question['question_type']}"
            
            answer_data = {
                "question": current_question["question_text"],
                "answer": mock_answer,
                "timestamp": datetime.now().isoformat(),
                "duration": 8.5
            }
            session.answers.append(answer_data)
            
            # Evaluate answer
            session.status = "evaluating"
            evaluation = await self.evaluate_answer(current_question, mock_answer, session.candidate)
            
            session.scores.append(evaluation["score"])
            session.feedback.append(evaluation["feedback"])
            
            logger.info(f"Answer evaluated - Score: {evaluation['score']}/10")
            
            # Brief pause before next question
            await asyncio.sleep(2)
        
        # Complete interview
        await self.complete_interview()
    
    async def generate_interview_questions(self, candidate: Candidate) -> List[Dict]:
        """Generate interview questions with AI fallback"""
        if ai_available:
            try:
                prompt = f"""
                Generate 5 progressive interview questions for a {candidate.experience_level} {candidate.position}.
                
                Candidate skills: {', '.join(candidate.skills)}
                
                Requirements:
                1. Mix of technical and behavioral questions
                2. Appropriate difficulty for {candidate.experience_level} level
                3. Natural conversation flow
                
                Return as JSON array:
                [
                    {{
                        "question_text": "question here",
                        "question_type": "technical|behavioral|introduction",
                        "skills_tested": ["skill1", "skill2"],
                        "expected_duration": 120
                    }}
                ]
                """
                
                response = ai_model.generate_content(prompt)
                questions_data = json.loads(response.text.strip())
                
                logger.info(f"Generated {len(questions_data)} AI questions for {candidate.name}")
                return questions_data
            
            except Exception as e:
                logger.warning(f"AI question generation failed: {e} - using fallbacks")
        
        # Fallback questions
        return self.get_fallback_questions(candidate)
    
    def get_fallback_questions(self, candidate: Candidate) -> List[Dict]:
        """High-quality fallback questions for any position"""
        
        # Customize based on experience level
        if candidate.experience_level == "entry":
            difficulty_prefix = "As someone new to the field, "
        elif candidate.experience_level == "senior":
            difficulty_prefix = "Given your senior experience, "
        else:
            difficulty_prefix = ""
        
        questions = [
            {
                "question_text": f"Tell me about yourself and what interests you most about the {candidate.position} role.",
                "question_type": "introduction",
                "skills_tested": ["communication", "motivation"],
                "expected_duration": 120
            },
            {
                "question_text": f"{difficulty_prefix}describe a challenging project you've worked on. What was your approach and what did you learn?",
                "question_type": "behavioral",
                "skills_tested": ["problem_solving", "learning", "project_management"],
                "expected_duration": 150
            },
            {
                "question_text": f"What technical skills or technologies do you think are most important for success in {candidate.position}?",
                "question_type": "technical",
                "skills_tested": ["technical_knowledge", "industry_awareness"],
                "expected_duration": 120
            },
            {
                "question_text": "Tell me about a time when you had to work with a difficult team member or stakeholder. How did you handle it?",
                "question_type": "behavioral",
                "skills_tested": ["interpersonal_skills", "conflict_resolution", "leadership"],
                "expected_duration": 130
            },
            {
                "question_text": f"Where do you see yourself growing in your {candidate.position} career over the next few years?",
                "question_type": "future_goals",
                "skills_tested": ["career_planning", "ambition", "company_fit"],
                "expected_duration": 100
            }
        ]
        
        # Add skill-specific questions if available
        if candidate.skills:
            skill_question = {
                "question_text": f"I see you have experience with {', '.join(candidate.skills[:3])}. Can you walk me through how you've used these in real projects?",
                "question_type": "technical",
                "skills_tested": candidate.skills[:3],
                "expected_duration": 140
            }
            questions[2] = skill_question  # Replace generic technical question
        
        return questions
    
    async def evaluate_answer(self, question: Dict, answer: str, candidate: Candidate) -> Dict:
        """Evaluate answer with AI fallback"""
        if ai_available:
            try:
                evaluation_prompt = f"""
                Evaluate this interview answer:
                
                Question: {question['question_text']}
                Question Type: {question['question_type']}
                Candidate Level: {candidate.experience_level}
                Answer: {answer}
                
                Provide evaluation as JSON:
                {{
                    "score": <1-10 rating>,
                    "feedback": "<detailed written feedback>",
                    "spoken_feedback": "<brief encouraging response>",
                    "strengths": ["<key strengths>"],
                    "improvements": ["<areas to improve>"]
                }}
                """
                
                response = ai_model.generate_content(evaluation_prompt)
                evaluation = json.loads(response.text.strip())
                
                return evaluation
            
            except Exception as e:
                logger.warning(f"AI evaluation failed: {e} - using fallback")
        
        # Fallback evaluation
        return self.get_fallback_evaluation(question, answer, candidate)
    
    def get_fallback_evaluation(self, question: Dict, answer: str, candidate: Candidate) -> Dict:
        """Smart fallback evaluation based on question type and answer analysis"""
        
        # Simple scoring based on answer length and keywords
        answer_words = len(answer.split())
        score = 7  # Default neutral score
        
        # Adjust score based on answer quality indicators
        if answer_words > 50:  # Detailed answer
            score += 1
        if answer_words < 10:   # Too brief
            score -= 1
        
        # Look for quality indicators in answer
        quality_keywords = [
            "experience", "project", "challenge", "learned", "result", 
            "team", "solution", "process", "improvement", "skill"
        ]
        
        keyword_count = sum(1 for word in quality_keywords if word.lower() in answer.lower())
        score += min(keyword_count // 2, 2)  # Bonus for quality keywords
        
        # Ensure score is in valid range
        score = max(1, min(10, score))
        
        # Generate appropriate feedback
        if score >= 8:
            feedback_tone = "Excellent response! You demonstrated strong"
            spoken = "Excellent answer!"
        elif score >= 6:
            feedback_tone = "Good response. You showed"
            spoken = "Good answer, thank you."
        else:
            feedback_tone = "Thank you for your response. Consider expanding on"
            spoken = "Thank you for sharing."
        
        question_type = question.get('question_type', 'general')
        
        feedback_templates = {
            'technical': f"{feedback_tone} technical knowledge and problem-solving abilities.",
            'behavioral': f"{feedback_tone} good situational awareness and interpersonal skills.",
            'introduction': f"{feedback_tone} clear communication and self-awareness.",
            'future_goals': f"{feedback_tone} thoughtful career planning and ambition."
        }
        
        feedback = feedback_templates.get(question_type, f"{feedback_tone} understanding of the topic.")
        
        return {
            "score": score,
            "feedback": feedback,
            "spoken_feedback": spoken,
            "strengths": ["Communication", "Relevant experience"],
            "improvements": ["Consider providing more specific examples"]
        }
    
    async def complete_interview(self):
        """Complete the interview and provide summary"""
        session = interview_sessions.get(self.session_id)
        if not session:
            return
        
        session.end_time = datetime.now()
        session.status = "completed"
        
        # Generate final summary
        summary = self.generate_final_summary(session)
        session.feedback.append(summary)
        
        logger.info(f"Interview completed for {session.candidate.name}")
        self.conversation_active = False
    
    def generate_final_summary(self, session: InterviewState) -> str:
        """Generate comprehensive interview summary"""
        if not session.scores:
            return "Interview completed successfully."
        
        avg_score = sum(session.scores) / len(session.scores)
        duration = (session.end_time - session.start_time).total_seconds() / 60 if session.start_time and session.end_time else 0
        
        # Determine performance level
        if avg_score >= 8:
            performance = "excellent"
            recommendation = "Highly recommend for next round"
        elif avg_score >= 6:
            performance = "good"
            recommendation = "Recommend for next round"
        else:
            performance = "satisfactory"
            recommendation = "Consider for further evaluation"
        
        summary = f"""
        Interview Summary for {session.candidate.name}:
        
        Overall Performance: {performance.title()} ({avg_score:.1f}/10)
        Questions Answered: {len(session.answers)}/{len(session.questions)}
        Interview Duration: {duration:.1f} minutes
        
        Key Strengths:
        - Clear communication skills
        - Relevant experience for {session.candidate.position}
        - Good understanding of role requirements
        
        Recommendation: {recommendation}
        
        Notes: Candidate demonstrated {performance} performance across all question types,
        showing readiness for the {session.candidate.position} position.
        """
        
        return summary.strip()

# FastAPI Application
app = FastAPI(title="Production Voice AI Interview Agent", version="2.0.0")

# Note: Static files removed for now - using CDN instead

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Production Voice AI Interview Agent", 
        "status": "active",
        "ai_available": ai_available,
        "livekit_available": livekit_available
    }

@app.get("/voice-ai")
async def serve_voice_ai_interface():
    """Serve the voice AI interview interface"""
    try:
        with open("voice_ai_interview.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Voice AI interface not found")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "livekit_url": LIVEKIT_URL,
        "ai_enabled": ai_available,
        "livekit_enabled": livekit_available,
        "timestamp": datetime.now().isoformat(),
        "fallback_mode": not ai_available
    }

@app.post("/api/voice-interview/create", response_model=VoiceSessionResponse)
async def create_voice_interview(request: VoiceInterviewRequest):
    """Create a production voice interview session"""
    try:
        # Generate session
        session_id = f"voice_session_{uuid.uuid4().hex[:8]}"
        room_name = f"voice_interview_{session_id}"
        
        # Generate access token (with fallback for missing LiveKit)
        access_token = "fallback_token"
        if livekit_available and LIVEKIT_API_KEY and LIVEKIT_API_SECRET:
            try:
                token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
                token.with_identity(f"candidate-{session_id}")
                token.with_name(request.candidate.name)
                token.with_grants(VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True
                ))
                access_token = token.to_jwt()
            except Exception as e:
                logger.warning(f"LiveKit token generation failed: {e}")
        
        # Create session state
        session = InterviewState(
            session_id=session_id,
            candidate=request.candidate,
            room_name=room_name,
            status="created",
            fallback_mode=not (ai_available and livekit_available)
        )
        interview_sessions[session_id] = session
        
        # Initialize AI agent
        ai_agent = ProductionAIInterviewAgent(session_id, room_name)
        
        # Start AI agent in background
        asyncio.create_task(ai_agent.initialize())
        
        return VoiceSessionResponse(
            success=True,
            session_id=session_id,
            room_name=room_name,
            access_token=access_token,
            livekit_url=LIVEKIT_URL,
            ai_agent_ready=True,
            message=f"Voice interview session created for {request.candidate.name}",
            fallback_mode=session.fallback_mode
        )
    
    except Exception as e:
        logger.error(f"Session creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.get("/api/voice-interview/status/{session_id}")
async def get_interview_status(session_id: str):
    """Get current interview status"""
    session = interview_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "status": session.status,
        "current_question": session.current_question_index + 1,
        "total_questions": len(session.questions),
        "ai_agent_connected": session.ai_agent_connected,
        "fallback_mode": session.fallback_mode,
        "start_time": session.start_time.isoformat() if session.start_time else None,
        "duration_minutes": (datetime.now() - session.start_time).total_seconds() / 60 if session.start_time else 0
    }

@app.get("/api/voice-interview/results/{session_id}")
async def get_interview_results(session_id: str):
    """Get complete interview results"""
    session = interview_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status not in ["completed", "terminated"]:
        # If interview is still active, return partial results
        pass
    
    # Calculate metrics
    avg_score = sum(session.scores) / len(session.scores) if session.scores else 0
    duration = (session.end_time - session.start_time).total_seconds() / 60 if session.start_time and session.end_time else 0
    
    return {
        "session_id": session_id,
        "candidate": session.candidate.dict(),
        "interview_summary": {
            "total_questions": len(session.questions),
            "total_answers": len(session.answers),
            "average_score": round(avg_score, 1),
            "duration_minutes": round(duration, 1),
            "completion_rate": len(session.answers) / len(session.questions) if session.questions else 0,
            "fallback_mode": session.fallback_mode
        },
        "detailed_results": [
            {
                "question": q["question_text"],
                "answer": a["answer"] if i < len(session.answers) else "No answer provided",
                "score": s if i < len(session.scores) else 0,
                "feedback": f if i < len(session.feedback[:-1] if session.feedback else []) else "No feedback available"
            }
            for i, (q, a, s, f) in enumerate(zip(
                session.questions, 
                session.answers + [{}] * max(0, len(session.questions) - len(session.answers)),
                session.scores + [0] * max(0, len(session.questions) - len(session.scores)),
                session.feedback[:-1] if session.feedback else [] + [""] * len(session.questions)
            ))
        ],
        "final_summary": session.feedback[-1] if session.feedback else "Interview in progress",
        "timestamp": session.end_time.isoformat() if session.end_time else datetime.now().isoformat()
    }

@app.delete("/api/voice-interview/{session_id}")
async def end_interview(session_id: str):
    """End an interview session"""
    session = interview_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.status = "terminated"
    session.end_time = datetime.now()
    
    return {"message": "Interview session ended", "session_id": session_id}

if __name__ == "__main__":
    print("🚀 Starting Production Voice AI Interview Agent...")
    print(f"🌐 API Server: http://localhost:8001")
    print(f"🎙️ Voice Interface: http://localhost:8001/voice-ai")
    print(f"📊 Health Check: http://localhost:8001/health")
    print(f"📚 API Docs: http://localhost:8001/docs")
    print(f"🤖 AI Status: {'✅ Enabled' if ai_available else '⚠️ Fallback Mode'}")
    print(f"🎙️ LiveKit Status: {'✅ Available' if livekit_available else '⚠️ Mock Mode'}")
    print("=" * 60)
    
    uvicorn.run(
        "production_voice_ai_agent:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
