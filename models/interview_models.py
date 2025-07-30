from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"

class InterviewStatus(str, Enum):
    CREATED = "created"
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class QuestionType(str, Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SITUATIONAL = "situational"
    CODING = "coding"

class Candidate(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    position: str
    experience_level: ExperienceLevel
    resume_content: Optional[str] = None
    skills: Optional[List[str]] = []
    created_at: Optional[datetime] = None

class Question(BaseModel):
    id: Optional[str] = None
    session_id: str
    question_text: str
    question_type: QuestionType
    difficulty_level: int  # 1-5
    expected_duration: int  # in seconds
    order_index: int
    is_asked: bool = False
    asked_at: Optional[datetime] = None

class Answer(BaseModel):
    id: Optional[str] = None
    session_id: str
    question_id: str
    answer_text: str
    duration: int  # in seconds
    submitted_at: datetime
    audio_url: Optional[str] = None

class Feedback(BaseModel):
    id: Optional[str] = None
    answer_id: str
    session_id: str
    score: int  # 1-5
    feedback_text: str
    criteria_scores: Dict[str, int]  # {"technical": 4, "communication": 5, ...}
    strengths: List[str]
    improvements: List[str]
    evaluated_at: datetime

class InterviewSession(BaseModel):
    id: Optional[str] = None
    candidate: Candidate
    status: InterviewStatus
    room_name: str
    current_question_index: int = 0
    total_questions: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    pause_duration: int = 0  # total paused time in seconds
    interview_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: Optional[datetime] = None

class InterviewSummary(BaseModel):
    session_id: str
    candidate_name: str
    position: str
    overall_score: float  # Average of all scores
    total_duration: int  # in seconds
    questions_asked: int
    category_scores: Dict[str, float]  # {"technical": 4.2, "behavioral": 3.8}
    strengths: List[str]
    areas_for_improvement: List[str]
    recommendation: str  # "hire", "consider", "reject"
    detailed_feedback: str
    generated_at: datetime

# Request/Response models for API
class SessionCreateRequest(BaseModel):
    candidate: Candidate
    interview_type: str = "technical"
    position_requirements: Optional[List[str]] = []

class SessionResponse(BaseModel):
    session_id: str
    room_name: str
    participant_token: str
    agent_token: str
    livekit_url: str
    status: InterviewStatus

class StartInterviewRequest(BaseModel):
    session_id: str

class StartInterviewResponse(BaseModel):
    success: bool
    first_question: Question
    total_questions: int
    estimated_duration: int  # in minutes

class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer_text: str
    duration: int

class SubmitAnswerResponse(BaseModel):
    success: bool
    feedback: Feedback
    next_question: Optional[Question] = None
    is_complete: bool = False
    session_summary: Optional[InterviewSummary] = None

class JoinSessionRequest(BaseModel):
    participant_name: Optional[str] = None

class JoinSessionResponse(BaseModel):
    success: bool
    access_token: str
    livekit_url: str
    room_name: str
    session_status: InterviewStatus
