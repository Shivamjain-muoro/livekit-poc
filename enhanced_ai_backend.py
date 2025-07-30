"""
Enhanced AI Interview Backend with Full LiveKit and LLM Integration
"""
import os
import uuid
import json
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from livekit.api import AccessToken
from livekit.api.access_token import VideoGrants
from datetime import datetime, timedelta
import uvicorn
import asyncio
from typing import Dict, List

# Import our models
from models.interview_models import (
    Candidate, SessionCreateRequest, SessionResponse, 
    StartInterviewRequest, StartInterviewResponse,
    SubmitAnswerRequest, SubmitAnswerResponse,
    JoinSessionRequest, JoinSessionResponse,
    ExperienceLevel, Question, QuestionType, Feedback
)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# FastAPI app
app = FastAPI(title="AI Interview System - Full Integration", version="3.0")

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

# Configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Google Gemini AI
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    print("✅ Google Gemini AI initialized")
else:
    model = None
    print("⚠️ No Google API key found, using fallback question generation")

# Storage
sessions = {}

class AIInterviewManager:
    """Manages AI-powered interview generation and evaluation"""
    
    def __init__(self, llm_model=None):
        self.model = llm_model
    
    def generate_personalized_questions(self, candidate: Candidate, num_questions: int = 5) -> List[dict]:
        """Generate personalized questions based on candidate profile"""
        if not self.model:
            return self._get_fallback_questions(candidate, num_questions)
        
        try:
            prompt = f"""
            You are an expert technical interviewer. Generate {num_questions} personalized interview questions for this candidate:

            Position: {candidate.position}
            Experience Level: {candidate.experience_level}
            Skills: {', '.join(candidate.skills) if candidate.skills else 'Not specified'}
            Name: {candidate.name}

            Requirements:
            1. Mix technical and behavioral questions appropriate for {candidate.experience_level} level
            2. Focus on skills: {', '.join(candidate.skills) if candidate.skills else 'general skills'}
            3. Questions should be challenging but fair for their experience level
            4. Include scenario-based questions relevant to {candidate.position}
            5. Each question should allow for 2-3 minute answers

            Format each question as:
            Question X: [Question text]
            Type: [technical/behavioral/situational]
            Expected Skills: [relevant skills being tested]

            Generate exactly {num_questions} questions.
            """
            
            response = self.model.generate_content(prompt)
            questions_text = response.text
            
            return self._parse_generated_questions(questions_text, candidate)
            
        except Exception as e:
            print(f"Error generating questions: {e}")
            return self._get_fallback_questions(candidate, num_questions)
    
    def _parse_generated_questions(self, questions_text: str, candidate: Candidate) -> List[dict]:
        """Parse AI-generated questions into structured format"""
        questions = []
        lines = questions_text.strip().split('\n')
        current_question = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('Question'):
                if current_question:
                    questions.append(self._format_question(current_question, candidate, len(questions) + 1))
                current_question = {'text': line.split(':', 1)[1].strip() if ':' in line else line}
            elif line.startswith('Type:'):
                current_question['type'] = line.split(':', 1)[1].strip()
            elif line.startswith('Expected Skills:'):
                current_question['skills'] = line.split(':', 1)[1].strip()
        
        # Add the last question
        if current_question:
            questions.append(self._format_question(current_question, candidate, len(questions) + 1))
        
        return questions[:5]  # Ensure we have exactly 5 questions
    
    def _format_question(self, question_data: dict, candidate: Candidate, order: int) -> dict:
        """Format a question into our standard structure"""
        question_type = question_data.get('type', 'technical').lower()
        
        return {
            "id": f"q_{uuid.uuid4().hex[:8]}",
            "session_id": "",  # Will be set later
            "question_text": question_data.get('text', ''),
            "question_type": question_type,
            "difficulty_level": self._get_difficulty_level(candidate.experience_level),
            "expected_duration": 120,  # 2 minutes
            "order_index": order,
            "is_asked": False,
            "skills_tested": question_data.get('skills', ''),
            "asked_at": None
        }
    
    def _get_difficulty_level(self, experience_level: str) -> int:
        """Map experience level to difficulty"""
        mapping = {
            "entry": 2,
            "mid": 3,
            "senior": 4,
            "lead": 5
        }
        return mapping.get(experience_level, 3)
    
    def _get_fallback_questions(self, candidate: Candidate, num_questions: int) -> List[dict]:
        """Fallback questions when AI is not available"""
        position_lower = candidate.position.lower()
        is_technical = any(word in position_lower for word in ["engineer", "developer", "programmer", "data", "scientist"])
        
        if is_technical:
            base_questions = [
                "Explain the difference between synchronous and asynchronous programming and when you would use each.",
                "Describe a challenging technical problem you solved recently. What was your approach?",
                "How do you ensure code quality and maintainability in your projects?",
                "Tell me about a time you had to learn a new technology quickly. How did you approach it?",
                "How do you handle debugging complex issues in production environments?"
            ]
        else:
            base_questions = [
                "Tell me about a challenging project you led and how you managed it.",
                "How do you prioritize tasks when everything seems urgent?",
                "Describe a time you had to work with a difficult team member. How did you handle it?",
                "What strategies do you use to stay updated in your field?",
                "Tell me about a time you had to make a decision with incomplete information."
            ]
        
        questions = []
        for i, text in enumerate(base_questions[:num_questions]):
            questions.append({
                "id": f"q_{uuid.uuid4().hex[:8]}",
                "session_id": "",
                "question_text": text,
                "question_type": "technical" if is_technical else "behavioral",
                "difficulty_level": self._get_difficulty_level(candidate.experience_level),
                "expected_duration": 120,
                "order_index": i + 1,
                "is_asked": False,
                "skills_tested": ', '.join(candidate.skills) if candidate.skills else "general",
                "asked_at": None
            })
        
        return questions
    
    def evaluate_answer(self, question: dict, answer: str, candidate: Candidate) -> dict:
        """Evaluate an answer using AI"""
        if not self.model or not answer or answer.strip() == "No speech detected":
            return self._get_fallback_evaluation(question, answer)
        
        try:
            prompt = f"""
            You are an expert interviewer evaluating a candidate's response. Please provide a detailed assessment:

            Candidate Profile:
            - Position: {candidate.position}
            - Experience Level: {candidate.experience_level}
            - Skills: {', '.join(candidate.skills) if candidate.skills else 'Not specified'}

            Question Asked: {question['question_text']}
            Question Type: {question['question_type']}
            Skills Being Tested: {question.get('skills_tested', 'general')}

            Candidate's Answer: {answer}

            Please evaluate on these criteria and provide scores (1-10):
            1. Technical Accuracy (if applicable)
            2. Communication Clarity
            3. Problem-Solving Approach
            4. Depth of Knowledge
            5. Relevance to Question

            Format your response as:
            SCORES:
            Technical Accuracy: X/10
            Communication Clarity: X/10
            Problem-Solving: X/10
            Depth of Knowledge: X/10
            Relevance: X/10

            FEEDBACK:
            [Detailed feedback about the answer]

            STRENGTHS:
            - [List 2-3 strengths observed]

            IMPROVEMENTS:
            - [List 2-3 areas for improvement]

            OVERALL SCORE: X/10
            """
            
            response = self.model.generate_content(prompt)
            return self._parse_evaluation(response.text, question, answer)
            
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            return self._get_fallback_evaluation(question, answer)
    
    def _parse_evaluation(self, evaluation_text: str, question: dict, answer: str) -> dict:
        """Parse AI evaluation into structured format"""
        lines = evaluation_text.strip().split('\n')
        scores = {}
        feedback = ""
        strengths = []
        improvements = []
        overall_score = 7
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('SCORES:'):
                current_section = 'scores'
            elif line.startswith('FEEDBACK:'):
                current_section = 'feedback'
            elif line.startswith('STRENGTHS:'):
                current_section = 'strengths'
            elif line.startswith('IMPROVEMENTS:'):
                current_section = 'improvements'
            elif line.startswith('OVERALL SCORE:'):
                try:
                    overall_score = int(line.split(':')[1].split('/')[0].strip())
                except:
                    overall_score = 7
            elif current_section == 'scores' and ':' in line:
                parts = line.split(':')
                if len(parts) == 2:
                    score_name = parts[0].strip()
                    try:
                        score_value = int(parts[1].split('/')[0].strip())
                        scores[score_name] = score_value
                    except:
                        pass
            elif current_section == 'feedback' and line:
                feedback += line + " "
            elif current_section == 'strengths' and line.startswith('-'):
                strengths.append(line[1:].strip())
            elif current_section == 'improvements' and line.startswith('-'):
                improvements.append(line[1:].strip())
        
        return {
            "id": f"f_{uuid.uuid4().hex[:8]}",
            "answer_id": f"a_{uuid.uuid4().hex[:8]}",
            "session_id": question.get('session_id', ''),
            "score": overall_score,
            "feedback_text": feedback.strip(),
            "criteria_scores": scores,
            "strengths": strengths if strengths else ["Clear communication", "Good understanding"],
            "improvements": improvements if improvements else ["Consider more examples", "Elaborate on key points"],
            "evaluated_at": datetime.now()
        }
    
    def _get_fallback_evaluation(self, question: dict, answer: str) -> dict:
        """Fallback evaluation when AI is not available"""
        # Simple evaluation based on answer length and basic criteria
        if not answer or answer.strip() == "No speech detected":
            score = 3
            feedback = "No meaningful response detected. Please try to provide a verbal answer."
            strengths = ["Participation in interview"]
            improvements = ["Provide verbal responses", "Speak clearly into microphone"]
        else:
            word_count = len(answer.split())
            if word_count < 10:
                score = 4
                feedback = "Response was very brief. Consider providing more detail and examples."
            elif word_count < 30:
                score = 6
                feedback = "Good response with room for more detail and specific examples."
            else:
                score = 7
                feedback = "Comprehensive response demonstrating good communication skills."
            
            strengths = ["Clear communication", "Engaged participation"]
            improvements = ["Provide specific examples", "Elaborate on technical details"]
        
        return {
            "id": f"f_{uuid.uuid4().hex[:8]}",
            "answer_id": f"a_{uuid.uuid4().hex[:8]}",
            "session_id": question.get('session_id', ''),
            "score": score,
            "feedback_text": feedback,
            "criteria_scores": {
                "Communication Clarity": score,
                "Content Quality": max(1, score - 1),
                "Relevance": score
            },
            "strengths": strengths,
            "improvements": improvements,
            "evaluated_at": datetime.now()
        }

# Initialize AI Manager
ai_manager = AIInterviewManager(model)

def generate_livekit_token(room_name: str, participant_identity: str, is_admin: bool = False) -> str:
    """Generate LiveKit access token"""
    try:
        token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        token.with_identity(participant_identity)
        token.with_name(participant_identity)
        
        grants = VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True
        )
        
        if is_admin:
            grants.room_admin = True
            grants.room_create = True
        
        token.with_grants(grants)
        
        # Token valid for 6 hours
        token.with_ttl(timedelta(hours=6))
        
        return token.to_jwt()
    except Exception as e:
        print(f"Error generating LiveKit token: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate access token")

@app.get("/")
async def root():
    return {
        "message": "Enhanced AI Interview System with Full Integration", 
        "status": "running",
        "features": {
            "livekit_integration": True,
            "ai_question_generation": bool(model),
            "ai_answer_evaluation": bool(model),
            "real_time_audio": True
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "livekit_url": LIVEKIT_URL,
        "ai_enabled": bool(model)
    }

@app.get("/live-local")
async def serve_live_local():
    return FileResponse("enhanced_interview_ui.html")

@app.get("/live-enhanced")
async def serve_enhanced():
    return FileResponse("enhanced_interview_ui.html")

@app.post("/api/interview/create-session", response_model=SessionResponse)
async def create_session(request: SessionCreateRequest):
    """Create a new interview session with LiveKit room"""
    try:
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        room_name = f"interview_{session_id}"
        
        # Generate tokens
        candidate_token = generate_livekit_token(room_name, f"candidate_{session_id}")
        agent_token = generate_livekit_token(room_name, f"agent_{session_id}", is_admin=True)
        
        # Generate personalized questions using AI
        questions = ai_manager.generate_personalized_questions(request.candidate)
        
        # Update session IDs in questions
        for question in questions:
            question["session_id"] = session_id
        
        # Store session
        sessions[session_id] = {
            "id": session_id,
            "candidate": request.candidate,
            "room_name": room_name,
            "status": "created",
            "questions": questions,
            "answers": [],
            "feedback": [],
            "current_question_index": 0,
            "created_at": datetime.now(),
            "tokens": {
                "candidate": candidate_token,
                "agent": agent_token
            }
        }
        
        return SessionResponse(
            session_id=session_id,
            room_name=room_name,
            participant_token=candidate_token,
            agent_token=agent_token,
            livekit_url=LIVEKIT_URL,
            status="created"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.post("/api/interview/start", response_model=StartInterviewResponse)
async def start_interview(request: StartInterviewRequest):
    """Start the interview session"""
    try:
        if request.session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = sessions[request.session_id]
        session["status"] = "started"
        session["start_time"] = datetime.now()
        
        # Get first question
        first_question = session["questions"][0] if session["questions"] else None
        if not first_question:
            raise HTTPException(status_code=500, detail="No questions generated for this session")
        
        # Mark first question as asked
        first_question["is_asked"] = True
        first_question["asked_at"] = datetime.now()
        session["current_question_index"] = 1
        
        # Convert to Question object
        question_obj = Question(
            id=first_question["id"],
            session_id=first_question["session_id"],
            question_text=first_question["question_text"],
            question_type=QuestionType.TECHNICAL if first_question["question_type"] == "technical" else QuestionType.BEHAVIORAL,
            difficulty_level=first_question["difficulty_level"],
            expected_duration=first_question["expected_duration"],
            order_index=first_question["order_index"],
            is_asked=True,
            asked_at=datetime.now()
        )
        
        return StartInterviewResponse(
            success=True,
            first_question=question_obj,
            total_questions=len(session["questions"]),
            estimated_duration=len(session["questions"]) * 3  # 3 minutes per question
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")

@app.post("/api/interview/submit-answer", response_model=SubmitAnswerResponse)
async def submit_answer(request: SubmitAnswerRequest):
    """Submit and evaluate an answer"""
    try:
        if request.session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = sessions[request.session_id]
        
        # Find the question
        current_question = None
        for q in session["questions"]:
            if q["id"] == request.question_id:
                current_question = q
                break
        
        if not current_question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Store the answer
        answer = {
            "id": f"a_{uuid.uuid4().hex[:8]}",
            "session_id": request.session_id,
            "question_id": request.question_id,
            "answer_text": request.answer_text,
            "duration": request.duration,
            "submitted_at": datetime.now()
        }
        session["answers"].append(answer)
        
        # Evaluate the answer using AI
        feedback = ai_manager.evaluate_answer(current_question, request.answer_text, session["candidate"])
        feedback["answer_id"] = answer["id"]
        feedback["session_id"] = request.session_id
        
        session["feedback"].append(feedback)
        
        # Check if interview is complete
        is_complete = session["current_question_index"] >= len(session["questions"])
        next_question = None
        
        if not is_complete:
            # Get next question
            next_q_data = session["questions"][session["current_question_index"]]
            next_q_data["is_asked"] = True
            next_q_data["asked_at"] = datetime.now()
            session["current_question_index"] += 1
            
            next_question = Question(
                id=next_q_data["id"],
                session_id=next_q_data["session_id"],
                question_text=next_q_data["question_text"],
                question_type=QuestionType.TECHNICAL if next_q_data["question_type"] == "technical" else QuestionType.BEHAVIORAL,
                difficulty_level=next_q_data["difficulty_level"],
                expected_duration=next_q_data["expected_duration"],
                order_index=next_q_data["order_index"],
                is_asked=True,
                asked_at=datetime.now()
            )
        else:
            session["status"] = "completed"
            session["end_time"] = datetime.now()
        
        # Create Feedback object
        feedback_obj = Feedback(
            id=feedback["id"],
            answer_id=feedback["answer_id"],
            session_id=feedback["session_id"],
            score=feedback["score"],
            feedback_text=feedback["feedback_text"],
            criteria_scores=feedback["criteria_scores"],
            strengths=feedback["strengths"],
            improvements=feedback["improvements"],
            evaluated_at=feedback["evaluated_at"]
        )
        
        return SubmitAnswerResponse(
            success=True,
            feedback=feedback_obj,
            next_question=next_question,
            is_complete=is_complete
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit answer: {str(e)}")

@app.get("/api/interview/feedback/{session_id}")
async def get_interview_feedback(session_id: str):
    """Generate comprehensive interview feedback"""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = sessions[session_id]
        feedback_list = session.get("feedback", [])
        
        if not feedback_list:
            # Generate basic feedback if no AI feedback available
            num_answers = len(session["answers"])
            overall_score = min(90, 60 + (num_answers * 5))
            
            return {
                "session_id": session_id,
                "candidate_name": session["candidate"].name,
                "position": session["candidate"].position,
                "overall_score": overall_score,
                "total_questions": len(session["questions"]),
                "total_answers": num_answers,
                "detailed_feedback": "Thank you for completing the interview! Your responses demonstrated good engagement with the questions.",
                "strengths": ["Clear communication", "Active participation"],
                "improvements": ["Consider providing more specific examples", "Elaborate on technical details"],
                "generated_at": datetime.now()
            }
        
        # Calculate overall metrics
        total_score = sum(f["score"] for f in feedback_list)
        overall_score = (total_score / len(feedback_list)) * 10  # Convert to percentage
        
        # Aggregate strengths and improvements
        all_strengths = []
        all_improvements = []
        
        for f in feedback_list:
            all_strengths.extend(f["strengths"])
            all_improvements.extend(f["improvements"])
        
        # Remove duplicates while preserving order
        unique_strengths = list(dict.fromkeys(all_strengths))[:5]
        unique_improvements = list(dict.fromkeys(all_improvements))[:5]
        
        # Generate summary feedback
        detailed_feedback = f"Excellent work completing the {len(session['questions'])}-question interview! "
        detailed_feedback += f"Your overall performance shows strong {session['candidate'].experience_level}-level capabilities. "
        detailed_feedback += "Key highlights include strong communication skills and good technical understanding. "
        detailed_feedback += "Continue developing your expertise and consider the improvement suggestions for future growth."
        
        return {
            "session_id": session_id,
            "candidate_name": session["candidate"].name,
            "position": session["candidate"].position,
            "overall_score": round(overall_score, 1),
            "total_questions": len(session["questions"]),
            "total_answers": len(session["answers"]),
            "detailed_feedback": detailed_feedback,
            "strengths": unique_strengths,
            "improvements": unique_improvements,
            "category_scores": {
                f"Question {i+1}": f["score"] for i, f in enumerate(feedback_list)
            },
            "generated_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feedback: {str(e)}")

@app.get("/api/interview/sessions")
async def list_sessions():
    """List all interview sessions"""
    try:
        session_list = []
        for session_id, session in sessions.items():
            session_info = {
                "id": session_id,
                "candidate_name": session["candidate"].name,
                "position": session["candidate"].position,
                "status": session["status"],
                "created_at": session["created_at"],
                "questions_count": len(session["questions"]),
                "answers_count": len(session["answers"])
            }
            session_list.append(session_info)
        
        return {"sessions": session_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced AI Interview System with Full Integration...")
    print(f"🎯 LiveKit Server: {LIVEKIT_URL}")
    print(f"🔑 API Key: {LIVEKIT_API_KEY}")
    print(f"🤖 AI Model: {'Google Gemini' if model else 'Fallback Questions'}")
    print(f"📱 Local Interview: http://localhost:8002/live-local")
    print(f"📊 Health Check: http://localhost:8002/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)
