import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from models.interview_models import (
    InterviewSession, Candidate, Question, Answer, Feedback, 
    InterviewSummary, InterviewStatus, QuestionType
)
from llm.evaluator import InterviewEvaluator, QuestionGenerator

class InterviewManager:
    """Manages interview flow and database operations"""
    
    def __init__(self, db_path: str = "interview_sessions.db"):
        self.db_path = db_path
        self.evaluator = InterviewEvaluator()
        self.question_generator = QuestionGenerator()
        self._init_enhanced_database()
    
    def _init_enhanced_database(self):
        """Initialize enhanced database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if enhanced columns exist, if not, add them
        cursor.execute("PRAGMA table_info(sessions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Enhanced sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                participant_name TEXT,
                participant_email TEXT,
                position TEXT,
                experience_level TEXT,
                room_name TEXT,
                status TEXT DEFAULT 'created',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resume_content TEXT,
                interview_data TEXT
            )
        """)
        
        # Add missing columns to existing table (without DEFAULT for some columns due to SQLite limitations)
        if 'current_question_index' not in columns:
            cursor.execute("ALTER TABLE sessions ADD COLUMN current_question_index INTEGER DEFAULT 0")
        if 'total_questions' not in columns:
            cursor.execute("ALTER TABLE sessions ADD COLUMN total_questions INTEGER DEFAULT 0")
        if 'start_time' not in columns:
            cursor.execute("ALTER TABLE sessions ADD COLUMN start_time TIMESTAMP")
        if 'end_time' not in columns:
            cursor.execute("ALTER TABLE sessions ADD COLUMN end_time TIMESTAMP")
        if 'pause_duration' not in columns:
            cursor.execute("ALTER TABLE sessions ADD COLUMN pause_duration INTEGER DEFAULT 0")
        if 'updated_at' not in columns:
            cursor.execute("ALTER TABLE sessions ADD COLUMN updated_at TIMESTAMP")
        if 'skills' not in columns:
            cursor.execute("ALTER TABLE sessions ADD COLUMN skills TEXT")
        
        # Questions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                question_text TEXT,
                question_type TEXT,
                difficulty_level INTEGER,
                expected_duration INTEGER,
                order_index INTEGER,
                is_asked BOOLEAN DEFAULT FALSE,
                asked_at TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        """)
        
        # Answers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS answers (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                question_id TEXT,
                answer_text TEXT,
                duration INTEGER,
                submitted_at TIMESTAMP,
                audio_url TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (id),
                FOREIGN KEY (question_id) REFERENCES questions (id)
            )
        """)
        
        # Feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                answer_id TEXT,
                session_id TEXT,
                score INTEGER,
                feedback_text TEXT,
                criteria_scores TEXT,
                strengths TEXT,
                improvements TEXT,
                evaluated_at TIMESTAMP,
                FOREIGN KEY (answer_id) REFERENCES answers (id),
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def create_session(self, candidate: Candidate, interview_type: str = "technical") -> InterviewSession:
        """Create a new interview session with generated questions"""
        session_id = str(uuid.uuid4())
        room_name = f"interview-{session_id[:8]}"
        
        # Generate questions for the candidate
        questions = await self.question_generator.generate_questions(candidate, num_questions=5)
        
        # Create session object
        session = InterviewSession(
            id=session_id,
            candidate=candidate,
            status=InterviewStatus.CREATED,
            room_name=room_name,
            total_questions=len(questions),
            created_at=datetime.now(),
            interview_data={"interview_type": interview_type}
        )
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert session
        cursor.execute("""
            INSERT INTO sessions (
                id, participant_name, participant_email, position, experience_level,
                room_name, status, total_questions, created_at, interview_data, skills
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id, candidate.name, candidate.email, candidate.position,
            candidate.experience_level, room_name, session.status.value,
            session.total_questions, session.created_at,
            json.dumps(session.interview_data),
            json.dumps(candidate.skills) if candidate.skills else "[]"
        ))
        
        # Insert questions
        for question in questions:
            question.session_id = session_id
            question.id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO questions (
                    id, session_id, question_text, question_type, difficulty_level,
                    expected_duration, order_index
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                question.id, question.session_id, question.question_text,
                question.question_type.value, question.difficulty_level,
                question.expected_duration, question.order_index
            ))
        
        conn.commit()
        conn.close()
        
        return session
    
    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """Get session by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Convert row to session object
        candidate = Candidate(
            name=row[1],  # participant_name
            email=row[2],  # participant_email
            position=row[3],  # position
            experience_level=row[4],  # experience_level
            skills=json.loads(row[13]) if row[13] else []  # skills
        )
        
        # Handle datetime parsing more safely
        def safe_datetime_parse(dt_string):
            if not dt_string:
                return None
            try:
                return datetime.fromisoformat(dt_string)
            except (ValueError, TypeError):
                return None
        
        session = InterviewSession(
            id=row[0],  # id
            candidate=candidate,
            status=InterviewStatus(row[5]),  # status
            room_name=row[6],  # room_name
            current_question_index=row[7] if row[7] is not None else 0,  # current_question_index
            total_questions=row[8] if row[8] is not None else 0,  # total_questions
            start_time=safe_datetime_parse(row[9]),  # start_time
            end_time=safe_datetime_parse(row[10]),  # end_time
            pause_duration=row[11] if row[11] is not None else 0,  # pause_duration
            created_at=safe_datetime_parse(row[14]) or datetime.now(),  # created_at
            updated_at=safe_datetime_parse(row[15]),  # updated_at
            interview_data=json.loads(row[12]) if row[12] else {}  # interview_data
        )
        
        return session
    
    def get_session_questions(self, session_id: str) -> List[Question]:
        """Get all questions for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, session_id, question_text, question_type, difficulty_level, 
                   expected_duration, order_index, is_asked, asked_at
            FROM questions WHERE session_id = ? ORDER BY order_index
        """, (session_id,))
        rows = cursor.fetchall()
        conn.close()
        
        questions = []
        for row in rows:
            question = Question(
                id=row[0],
                session_id=row[1],
                question_text=row[2],
                question_type=QuestionType(row[3]),
                difficulty_level=row[4],
                expected_duration=row[5],
                order_index=row[6],
                is_asked=bool(row[7]),
                asked_at=datetime.fromisoformat(row[8]) if row[8] else None
            )
            questions.append(question)
        
        return questions
    
    def start_interview(self, session_id: str) -> Optional[Question]:
        """Start interview and return first question"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update session status
        cursor.execute("""
            UPDATE sessions 
            SET status = ?, start_time = ?, current_question_index = 1, updated_at = ?
            WHERE id = ?
        """, (InterviewStatus.IN_PROGRESS.value, datetime.now(), datetime.now(), session_id))
        
        # Get first question
        cursor.execute("""
            SELECT id, session_id, question_text, question_type, difficulty_level, 
                   expected_duration, order_index, is_asked, asked_at 
            FROM questions 
            WHERE session_id = ? AND order_index = 1
        """, (session_id,))
        row = cursor.fetchone()

        if row:
            # Mark question as asked
            cursor.execute("""
                UPDATE questions 
                SET is_asked = TRUE, asked_at = ?
                WHERE id = ?
            """, (datetime.now(), row[0]))
            
            question = Question(
                id=row[0],
                session_id=row[1],
                question_text=row[2],
                question_type=QuestionType(row[3]),
                difficulty_level=row[4],
                expected_duration=row[5],
                order_index=row[6],
                is_asked=True,
                asked_at=datetime.now()
            )
        else:
            question = None
        
        conn.commit()
        conn.close()
        
        return question
    
    async def submit_answer(self, session_id: str, question_id: str, 
                          answer_text: str, duration: int) -> tuple[Feedback, Optional[Question], bool]:
        """Submit answer, get evaluation, and return next question"""
        
        # Create answer record
        answer_id = str(uuid.uuid4())
        answer = Answer(
            id=answer_id,
            session_id=session_id,
            question_id=question_id,
            answer_text=answer_text,
            duration=duration,
            submitted_at=datetime.now()
        )
        
        # Get question and candidate for evaluation
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get question
        cursor.execute("""
            SELECT id, session_id, question_text, question_type, difficulty_level, 
                   expected_duration, order_index, is_asked, asked_at
            FROM questions WHERE id = ?
        """, (question_id,))
        q_row = cursor.fetchone()
        question = Question(
            id=q_row[0],
            session_id=q_row[1],
            question_text=q_row[2],
            question_type=QuestionType(q_row[3]),
            difficulty_level=q_row[4],
            expected_duration=q_row[5],
            order_index=q_row[6]
        )
        
        # Get candidate
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        s_row = cursor.fetchone()
        candidate = Candidate(
            name=s_row[1],
            email=s_row[2],
            position=s_row[3],
            experience_level=s_row[4]
        )
        
        # Save answer
        cursor.execute("""
            INSERT INTO answers (id, session_id, question_id, answer_text, duration, submitted_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (answer_id, session_id, question_id, answer_text, duration, answer.submitted_at))
        
        conn.commit()
        conn.close()
        
        # Evaluate answer
        feedback = await self.evaluator.evaluate_answer(question, answer, candidate)
        feedback.id = str(uuid.uuid4())
        
        # Save feedback
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedback (
                id, answer_id, session_id, score, feedback_text, 
                criteria_scores, strengths, improvements, evaluated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            feedback.id, answer_id, session_id, feedback.score, feedback.feedback_text,
            json.dumps(feedback.criteria_scores), json.dumps(feedback.strengths),
            json.dumps(feedback.improvements), feedback.evaluated_at
        ))
        
        # Get next question
        current_index = question.order_index
        cursor.execute("""
            SELECT id, session_id, question_text, question_type, difficulty_level, 
                   expected_duration, order_index, is_asked, asked_at
            FROM questions 
            WHERE session_id = ? AND order_index = ?
        """, (session_id, current_index + 1))
        next_row = cursor.fetchone()
        
        next_question = None
        is_complete = False
        
        if next_row:
            # Mark next question as asked
            cursor.execute("""
                UPDATE questions 
                SET is_asked = TRUE, asked_at = ?
                WHERE id = ?
            """, (datetime.now(), next_row[0]))
            
            # Update session current question index
            cursor.execute("""
                UPDATE sessions 
                SET current_question_index = ?, updated_at = ?
                WHERE id = ?
            """, (current_index + 1, datetime.now(), session_id))
            
            next_question = Question(
                id=next_row[0],
                session_id=next_row[1],
                question_text=next_row[2],
                question_type=QuestionType(next_row[3]),
                difficulty_level=next_row[4],
                expected_duration=next_row[5],
                order_index=next_row[6],
                is_asked=True,
                asked_at=datetime.now()
            )
        else:
            # Interview complete
            is_complete = True
            cursor.execute("""
                UPDATE sessions 
                SET status = ?, end_time = ?, updated_at = ?
                WHERE id = ?
            """, (InterviewStatus.COMPLETED.value, datetime.now(), datetime.now(), session_id))
        
        conn.commit()
        conn.close()
        
        return feedback, next_question, is_complete
    
    def generate_interview_summary(self, session_id: str) -> Optional[InterviewSummary]:
        """Generate comprehensive interview summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get session info
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        session_row = cursor.fetchone()
        
        if not session_row:
            return None
        
        # Get all feedback
        cursor.execute("""
            SELECT f.*, q.question_type FROM feedback f
            JOIN answers a ON f.answer_id = a.id
            JOIN questions q ON a.question_id = q.id
            WHERE f.session_id = ?
        """, (session_id,))
        feedback_rows = cursor.fetchall()
        
        conn.close()
        
        if not feedback_rows:
            return None
        
        # Calculate scores
        total_score = sum(row[3] for row in feedback_rows)  # score column
        overall_score = total_score / len(feedback_rows)
        
        # Category scores
        category_scores = {}
        category_counts = {}
        for row in feedback_rows:
            question_type = row[10]  # question_type from join
            if question_type not in category_scores:
                category_scores[question_type] = 0
                category_counts[question_type] = 0
            category_scores[question_type] += row[3]
            category_counts[question_type] += 1
        
        for category in category_scores:
            category_scores[category] = category_scores[category] / category_counts[category]
        
        # Collect strengths and improvements
        all_strengths = []
        all_improvements = []
        for row in feedback_rows:
            strengths = json.loads(row[6]) if row[6] else []
            improvements = json.loads(row[7]) if row[7] else []
            all_strengths.extend(strengths)
            all_improvements.extend(improvements)
        
        # Determine recommendation
        if overall_score >= 4.0:
            recommendation = "hire"
        elif overall_score >= 3.0:
            recommendation = "consider"
        else:
            recommendation = "reject"
        
        # Calculate duration
        start_time = datetime.fromisoformat(session_row[9]) if session_row[9] else datetime.now()
        end_time = datetime.fromisoformat(session_row[10]) if session_row[10] else datetime.now()
        duration = int((end_time - start_time).total_seconds())
        
        summary = InterviewSummary(
            session_id=session_id,
            candidate_name=session_row[1],
            position=session_row[3],
            overall_score=round(overall_score, 2),
            total_duration=duration,
            questions_asked=len(feedback_rows),
            category_scores=category_scores,
            strengths=list(set(all_strengths)),
            areas_for_improvement=list(set(all_improvements)),
            recommendation=recommendation,
            detailed_feedback=f"Overall performance was {'excellent' if overall_score >= 4 else 'good' if overall_score >= 3 else 'needs improvement'}.",
            generated_at=datetime.now()
        )
        
        return summary
