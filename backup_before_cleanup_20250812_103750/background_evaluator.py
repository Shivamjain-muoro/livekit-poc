"""
Background Interview Evaluation System
Processes interview data without blocking real-time conversation
"""

import asyncio
import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional
import google.generativeai as genai
from dataclasses import dataclass
import threading
import queue
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InterviewData:
    """Structure for interview data to be processed"""
    session_id: str
    candidate_name: str
    position: str
    question: str
    response: str
    timestamp: datetime
    response_duration: float = 0.0
    audio_quality: str = "good"

class BackgroundEvaluator:
    """
    Non-blocking background processor for interview evaluation
    Runs in separate thread to avoid interrupting real-time conversation
    """
    
    def __init__(self, google_api_key: str):
        self.google_api_key = google_api_key
        self.processing_queue = queue.Queue()
        self.is_running = False
        self.worker_thread = None
        self.db_path = self._get_db_path()
        self._init_database()
        
        if google_api_key:
            genai.configure(api_key=google_api_key)
            logger.info("✅ Background Evaluator: Google AI configured")
        
    def _get_db_path(self) -> str:
        """Get database path for interview storage"""
        os.makedirs("database", exist_ok=True)
        return os.path.join("database", "interview_evaluations.db")
    
    def _init_database(self):
        """Initialize comprehensive database schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS interview_sessions (
                        session_id TEXT PRIMARY KEY,
                        candidate_name TEXT,
                        position TEXT,
                        start_time TIMESTAMP,
                        end_time TIMESTAMP,
                        status TEXT DEFAULT 'active',
                        overall_score REAL DEFAULT 0.0,
                        technical_score REAL DEFAULT 0.0,
                        communication_score REAL DEFAULT 0.0,
                        cultural_fit_score REAL DEFAULT 0.0,
                        recommendation TEXT DEFAULT 'pending'
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS interview_exchanges (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        question TEXT,
                        response TEXT,
                        timestamp TIMESTAMP,
                        response_duration REAL,
                        audio_quality TEXT,
                        relevance_score REAL DEFAULT 0.0,
                        clarity_score REAL DEFAULT 0.0,
                        depth_score REAL DEFAULT 0.0,
                        ai_evaluation TEXT,
                        key_points TEXT,
                        concerns TEXT,
                        FOREIGN KEY (session_id) REFERENCES interview_sessions (session_id)
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS evaluation_summary (
                        session_id TEXT PRIMARY KEY,
                        total_questions INTEGER DEFAULT 0,
                        total_responses INTEGER DEFAULT 0,
                        avg_response_time REAL DEFAULT 0.0,
                        strong_areas TEXT,
                        improvement_areas TEXT,
                        detailed_feedback TEXT,
                        final_recommendation TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES interview_sessions (session_id)
                    )
                """)
                
                conn.commit()
                logger.info("✅ Background Evaluator: Database schema initialized")
                
        except Exception as e:
            logger.error(f"❌ Background Evaluator: Database init error: {e}")
    
    def start_background_processing(self):
        """Start the background processing thread"""
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
            self.worker_thread.start()
            logger.info("🚀 Background Evaluator: Started background processing")
    
    def stop_background_processing(self):
        """Stop the background processing"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info("🛑 Background Evaluator: Stopped background processing")
    
    def queue_for_evaluation(self, interview_data: InterviewData):
        """Add interview data to processing queue (non-blocking)"""
        try:
            self.processing_queue.put(interview_data, block=False)
            logger.info(f"📥 Background Evaluator: Queued data for session {interview_data.session_id}")
        except queue.Full:
            logger.warning("⚠️ Background Evaluator: Queue full, skipping evaluation")
    
    def _process_queue(self):
        """Background thread worker - processes evaluation queue"""
        logger.info("🔄 Background Evaluator: Processing thread started")
        
        while self.is_running:
            try:
                # Get data from queue with timeout
                interview_data = self.processing_queue.get(timeout=1.0)
                
                # Process the evaluation
                asyncio.run(self._evaluate_response(interview_data))
                
                # Mark task as done
                self.processing_queue.task_done()
                
            except queue.Empty:
                # No data to process, continue loop
                continue
            except Exception as e:
                logger.error(f"❌ Background Evaluator: Processing error: {e}")
    
    async def _evaluate_response(self, data: InterviewData):
        """Perform comprehensive evaluation of interview response"""
        try:
            logger.info(f"🧠 Background Evaluator: Evaluating response for {data.session_id}")
            
            # Store raw data first
            await self._store_raw_exchange(data)
            
            # Perform AI evaluation if available
            if self.google_api_key:
                evaluation = await self._ai_evaluate_response(data)
                await self._store_evaluation(data, evaluation)
            
            # Update session scores
            await self._update_session_scores(data.session_id)
            
            logger.info(f"✅ Background Evaluator: Completed evaluation for {data.session_id}")
            
        except Exception as e:
            logger.error(f"❌ Background Evaluator: Evaluation error: {e}")
    
    async def _store_raw_exchange(self, data: InterviewData):
        """Store the raw interview exchange"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Ensure session exists
                conn.execute("""
                    INSERT OR IGNORE INTO interview_sessions 
                    (session_id, candidate_name, position, start_time, status)
                    VALUES (?, ?, ?, ?, 'active')
                """, (data.session_id, data.candidate_name, data.position, data.timestamp))
                
                # Store the exchange
                conn.execute("""
                    INSERT INTO interview_exchanges 
                    (session_id, question, response, timestamp, response_duration, audio_quality)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (data.session_id, data.question, data.response, 
                     data.timestamp, data.response_duration, data.audio_quality))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Background Evaluator: Store exchange error: {e}")
    
    async def _ai_evaluate_response(self, data: InterviewData) -> Dict:
        """Use AI to evaluate the interview response"""
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            evaluation_prompt = f"""
            Evaluate this interview response professionally and objectively.
            
            Position: {data.position}
            Question: {data.question}
            Candidate Response: {data.response}
            
            Provide evaluation in this JSON format:
            {{
                "relevance_score": 0-10,
                "clarity_score": 0-10,
                "depth_score": 0-10,
                "key_points": ["point1", "point2"],
                "concerns": ["concern1"] or [],
                "evaluation_summary": "brief professional assessment",
                "strengths": ["strength1", "strength2"],
                "areas_for_improvement": ["area1"] or []
            }}
            
            Be fair, constructive, and professional.
            """
            
            response = model.generate_content(
                evaluation_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=800,
                    top_p=0.9
                )
            )
            
            # Parse JSON response
            evaluation_text = response.text.strip()
            if '{' in evaluation_text and '}' in evaluation_text:
                start = evaluation_text.find('{')
                end = evaluation_text.rfind('}') + 1
                evaluation_json = evaluation_text[start:end]
                return json.loads(evaluation_json)
            
            # Fallback evaluation
            return {
                "relevance_score": 7.0,
                "clarity_score": 7.0,
                "depth_score": 6.0,
                "key_points": ["Response provided"],
                "concerns": [],
                "evaluation_summary": "Standard response evaluation",
                "strengths": ["Participated in interview"],
                "areas_for_improvement": []
            }
            
        except Exception as e:
            logger.error(f"❌ Background Evaluator: AI evaluation error: {e}")
            return {
                "relevance_score": 5.0,
                "clarity_score": 5.0,
                "depth_score": 5.0,
                "key_points": [],
                "concerns": [],
                "evaluation_summary": f"Evaluation error: {str(e)}",
                "strengths": [],
                "areas_for_improvement": []
            }
    
    async def _store_evaluation(self, data: InterviewData, evaluation: Dict):
        """Store the AI evaluation results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE interview_exchanges 
                    SET relevance_score = ?, clarity_score = ?, depth_score = ?,
                        ai_evaluation = ?, key_points = ?, concerns = ?
                    WHERE session_id = ? AND question = ? AND timestamp = ?
                """, (
                    evaluation.get('relevance_score', 0),
                    evaluation.get('clarity_score', 0),
                    evaluation.get('depth_score', 0),
                    evaluation.get('evaluation_summary', ''),
                    json.dumps(evaluation.get('key_points', [])),
                    json.dumps(evaluation.get('concerns', [])),
                    data.session_id,
                    data.question,
                    data.timestamp
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Background Evaluator: Store evaluation error: {e}")
    
    async def _update_session_scores(self, session_id: str):
        """Update overall session scores based on all responses"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Calculate averages
                cursor = conn.execute("""
                    SELECT 
                        AVG(relevance_score) as avg_relevance,
                        AVG(clarity_score) as avg_clarity,
                        AVG(depth_score) as avg_depth,
                        AVG(response_duration) as avg_duration,
                        COUNT(*) as total_responses
                    FROM interview_exchanges 
                    WHERE session_id = ?
                """, (session_id,))
                
                result = cursor.fetchone()
                if result:
                    avg_relevance, avg_clarity, avg_depth, avg_duration, total_responses = result
                    
                    # Calculate overall scores
                    technical_score = (avg_relevance + avg_depth) / 2
                    communication_score = avg_clarity
                    overall_score = (technical_score + communication_score) / 2
                    
                    # Update session
                    conn.execute("""
                        UPDATE interview_sessions 
                        SET overall_score = ?, technical_score = ?, 
                            communication_score = ?
                        WHERE session_id = ?
                    """, (overall_score, technical_score, communication_score, session_id))
                    
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"❌ Background Evaluator: Update scores error: {e}")
    
    def get_session_report(self, session_id: str) -> Optional[Dict]:
        """Generate comprehensive session report"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get session info
                session_cursor = conn.execute("""
                    SELECT * FROM interview_sessions WHERE session_id = ?
                """, (session_id,))
                session_data = session_cursor.fetchone()
                
                if not session_data:
                    return None
                
                # Get all exchanges
                exchanges_cursor = conn.execute("""
                    SELECT * FROM interview_exchanges 
                    WHERE session_id = ? 
                    ORDER BY timestamp
                """, (session_id,))
                exchanges = exchanges_cursor.fetchall()
                
                # Build report
                report = {
                    "session_id": session_id,
                    "candidate_name": session_data[1],
                    "position": session_data[2],
                    "overall_score": session_data[6],
                    "technical_score": session_data[7],
                    "communication_score": session_data[8],
                    "total_questions": len(exchanges),
                    "exchanges": [
                        {
                            "question": ex[2],
                            "response": ex[3],
                            "relevance_score": ex[7],
                            "clarity_score": ex[8],
                            "depth_score": ex[9],
                            "evaluation": ex[10]
                        } for ex in exchanges
                    ]
                }
                
                return report
                
        except Exception as e:
            logger.error(f"❌ Background Evaluator: Report generation error: {e}")
            return None

# Global evaluator instance
_background_evaluator = None

def get_background_evaluator(google_api_key: str) -> BackgroundEvaluator:
    """Get or create the global background evaluator instance"""
    global _background_evaluator
    if _background_evaluator is None:
        _background_evaluator = BackgroundEvaluator(google_api_key)
        _background_evaluator.start_background_processing()
    return _background_evaluator

def queue_interview_data(session_id: str, candidate_name: str, position: str, 
                        question: str, response: str, google_api_key: str = None):
    """Quick function to queue interview data for background processing"""
    if google_api_key:
        evaluator = get_background_evaluator(google_api_key)
        interview_data = InterviewData(
            session_id=session_id,
            candidate_name=candidate_name,
            position=position,
            question=question,
            response=response,
            timestamp=datetime.now()
        )
        evaluator.queue_for_evaluation(interview_data)
