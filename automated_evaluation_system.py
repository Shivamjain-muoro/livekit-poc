"""
Automated Real-Time Evaluation System
Automatically evaluates and scores each exchange during the interview
No manual intervention required - everything happens automatically
"""

import json
import sqlite3
import os
import time
import threading
import queue
from datetime import datetime
import google.generativeai as genai
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create formatter for evaluation system
formatter = logging.Formatter('%(asctime)s - 🤖 %(levelname)s - %(message)s')

# Add file handler for evaluation logs
eval_handler = logging.FileHandler('evaluation.log')
eval_handler.setFormatter(formatter)
eval_handler.setLevel(logging.INFO)
logger.addHandler(eval_handler)

# Add console handler for important messages
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

# Filter out debug logs for media chunks
class MediaChunkFilter(logging.Filter):
    def filter(self, record):
        return 'mediaChunks' not in str(record.msg)

logger.addFilter(MediaChunkFilter())

class AutomatedEvaluationSystem:
    def __init__(self, google_api_key):
        """Initialize the automated evaluation system"""
        self.google_api_key = google_api_key
        if google_api_key:
            genai.configure(api_key=google_api_key)
            print("✅ AUTOMATED_EVAL: Google API configured")
        
        # Evaluation queue for real-time processing
        self.evaluation_queue = queue.Queue()
        self.evaluation_worker = None
        self.worker_running = False
        
        # Start background worker
        self.start_evaluation_worker()
        
        print("🚀 AUTOMATED_EVAL: System initialized and ready")
    
    def get_db_connection(self):
        """Get database connection"""
        os.makedirs("database", exist_ok=True)
        db_path = os.path.join("database", "interview_evaluations.db")
        return sqlite3.connect(db_path)
    
    def start_evaluation_worker(self):
        """Start background evaluation worker"""
        if self.worker_running:
            return
        
        self.worker_running = True
        self.evaluation_worker = threading.Thread(
            target=self._evaluation_worker_loop,
            daemon=True
        )
        self.evaluation_worker.start()
        print("🔄 AUTOMATED_EVAL: Background evaluation worker started")
    
    def stop_evaluation_worker(self):
        """Stop background evaluation worker"""
        self.worker_running = False
        if self.evaluation_worker:
            # Add poison pill to queue to wake up worker
            self.evaluation_queue.put(None)
            self.evaluation_worker.join(timeout=5)
        print("⏹️ AUTOMATED_EVAL: Background evaluation worker stopped")
    
    def _evaluation_worker_loop(self):
        """Background worker loop that processes evaluations"""
        print("🔄 AUTOMATED_EVAL: Evaluation worker loop started")
        
        while self.worker_running:
            try:
                # Get evaluation data from queue (blocking with timeout)
                eval_data = self.evaluation_queue.get(timeout=1)
                
                # Check for poison pill (shutdown signal)
                if eval_data is None:
                    break
                
                print(f"⚡ AUTOMATED_EVAL: Processing evaluation for session {eval_data['session_id']}")
                
                # Process the evaluation
                self._process_single_evaluation(eval_data)
                
                # Mark task as done
                self.evaluation_queue.task_done()
                
            except queue.Empty:
                # Timeout occurred, continue loop
                continue
            except Exception as e:
                logger.error(f"❌ AUTOMATED_EVAL: Error in worker loop: {e}")
                continue
        
        print("✅ AUTOMATED_EVAL: Evaluation worker loop finished")
    
    def _process_single_evaluation(self, eval_data):
        """Process a single evaluation automatically"""
        start_time = time.time()
        
        try:
            session_id = eval_data['session_id']
            question = eval_data['question']
            response = eval_data['response']
            response_duration = eval_data['response_duration']
            candidate_name = eval_data.get('candidate_name', 'Unknown')
            position = eval_data.get('position', 'Unknown')
            timestamp = eval_data.get('timestamp', datetime.now().isoformat())
            
            print(f"🔍 AUTOMATED_EVAL: Evaluating Q&A for session {session_id}")
            print(f"   📝 Question: {question[:100]}...")
            print(f"   💬 Response: {response[:100]}...")
            
            # First, store the raw exchange in database
            exchange_id = self._store_exchange(session_id, question, response, response_duration, timestamp)
            
            if not exchange_id:
                logger.error("Failed to store exchange, skipping evaluation")
                return
            
            # Generate AI evaluation
            evaluation_scores = self._generate_ai_evaluation(
                question, response, response_duration, candidate_name, position
            )
            
            # Update the exchange with evaluation scores
            self._update_exchange_with_evaluation(exchange_id, evaluation_scores)
            
            # Update session statistics
            self._update_session_statistics(session_id)
            
            processing_time = time.time() - start_time
            print(f"✅ AUTOMATED_EVAL: Completed evaluation in {processing_time:.2f}s")
            print(f"   📊 Overall Score: {evaluation_scores.get('overall_score', 0):.1f}/10")
            print(f"   🎯 Technical: {evaluation_scores.get('correctness_score', 0):.1f}/10")
            print(f"   💬 Communication: {evaluation_scores.get('clarity_score', 0):.1f}/10")
            
        except Exception as e:
            logger.error(f"❌ AUTOMATED_EVAL: Evaluation failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _store_exchange(self, session_id, question, response, response_duration, timestamp):
        """Store raw exchange in database and return exchange ID"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO interview_exchanges (
                        session_id, question, response, response_duration, timestamp
                    ) VALUES (?, ?, ?, ?, ?)
                """, (session_id, question, response, response_duration, timestamp))
                
                exchange_id = cursor.lastrowid
                conn.commit()
                
                print(f"💾 AUTOMATED_EVAL: Stored exchange {exchange_id} for session {session_id}")
                return exchange_id
                
        except Exception as e:
            logger.error(f"❌ AUTOMATED_EVAL: Failed to store exchange: {e}")
            return None
    
    def _generate_ai_evaluation(self, question, response, response_duration, candidate_name, position):
        """Generate AI evaluation scores using Gemini"""
        try:
            evaluation_prompt = f"""
            INTERVIEW EVALUATION TASK
            
            Candidate: {candidate_name}
            Position: {position}
            
            Question: {question}
            Response: {response}
            Response Time: {response_duration}s
            
            Evaluate this interview response and provide scores (0-10) for each criterion:
            
            SCORING CRITERIA:
            1. Correctness (0-10): Technical accuracy and factual correctness
            2. Completeness (0-10): How thoroughly the question was answered
            3. Clarity (0-10): Communication clarity and articulation
            4. Skill Relevance (0-10): Relevance to the job position
            5. Fluency (0-10): Language fluency and flow
            6. Confidence (0-10): Confidence level demonstrated
            
            SENTIMENT ANALYSIS (0-1 scale):
            - Positive sentiment (0-1)
            - Neutral sentiment (0-1) 
            - Negative sentiment (0-1)
            
            Provide response in this EXACT JSON format:
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
                "overall_assessment": "brief overall assessment",
                "overall_score": 0-10
            }}
            """
            
            if not self.google_api_key:
                # Fallback scoring if no API key
                return self._get_fallback_scores()
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            response_obj = model.generate_content(
                evaluation_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=1000
                )
            )
            
            evaluation_text = response_obj.text
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', evaluation_text, re.DOTALL)
            if json_match:
                evaluation_scores = json.loads(json_match.group())
                
                # Calculate overall score if not provided
                if 'overall_score' not in evaluation_scores:
                    evaluation_scores['overall_score'] = (
                        evaluation_scores.get('correctness_score', 0) +
                        evaluation_scores.get('completeness_score', 0) +
                        evaluation_scores.get('clarity_score', 0) +
                        evaluation_scores.get('skill_relevance_score', 0)
                    ) / 4
                
                return evaluation_scores
            else:
                logger.warning("Could not parse JSON from AI response, using fallback")
                return self._get_fallback_scores()
                
        except Exception as e:
            logger.error(f"❌ AUTOMATED_EVAL: AI evaluation failed: {e}")
            return self._get_fallback_scores()
    
    def _get_fallback_scores(self):
        """Fallback scores when AI evaluation fails"""
        return {
            "correctness_score": 7.0,
            "completeness_score": 7.0,
            "clarity_score": 7.0,
            "skill_relevance_score": 7.0,
            "fluency_score": 7.5,
            "confidence_score": 7.0,
            "sentiment_positive": 0.7,
            "sentiment_neutral": 0.3,
            "sentiment_negative": 0.0,
            "key_skills_demonstrated": ["communication", "technical knowledge"],
            "areas_of_concern": [],
            "follow_up_suggestions": ["probe deeper into technical details"],
            "overall_assessment": "Adequate response with room for improvement",
            "overall_score": 7.0
        }
    
    def _update_exchange_with_evaluation(self, exchange_id, evaluation_scores):
        """Update exchange with evaluation scores"""
        try:
            with self.get_db_connection() as conn:
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
                        overall_assessment = ?,
                        key_skills_demonstrated = ?,
                        areas_of_concern = ?,
                        follow_up_suggestions = ?,
                        overall_score = ?,
                        evaluated_at = ?
                    WHERE id = ?
                """, (
                    evaluation_scores.get("correctness_score", 0),
                    evaluation_scores.get("completeness_score", 0),
                    evaluation_scores.get("clarity_score", 0),
                    evaluation_scores.get("skill_relevance_score", 0),
                    evaluation_scores.get("fluency_score", 0),
                    evaluation_scores.get("confidence_score", 0),
                    evaluation_scores.get("sentiment_positive", 0),
                    evaluation_scores.get("sentiment_neutral", 0),
                    evaluation_scores.get("sentiment_negative", 0),
                    evaluation_scores.get("overall_assessment", ""),
                    json.dumps(evaluation_scores.get("key_skills_demonstrated", [])),
                    json.dumps(evaluation_scores.get("areas_of_concern", [])),
                    json.dumps(evaluation_scores.get("follow_up_suggestions", [])),
                    evaluation_scores.get("overall_score", 0),
                    datetime.now().isoformat(),
                    exchange_id
                ))
                conn.commit()
                print(f"✅ AUTOMATED_EVAL: Updated exchange {exchange_id} with evaluation scores")
                
        except Exception as e:
            logger.error(f"❌ AUTOMATED_EVAL: Failed to update exchange with evaluation: {e}")
    
    def _update_session_statistics(self, session_id):
        """Update session-level statistics based on all exchanges"""
        try:
            with self.get_db_connection() as conn:
                # Calculate averages from all exchanges in this session
                cursor = conn.execute("""
                    SELECT 
                        AVG(correctness_score) as avg_correctness,
                        AVG(completeness_score) as avg_completeness,
                        AVG(clarity_score) as avg_clarity,
                        AVG(skill_relevance_score) as avg_skill_relevance,
                        AVG(fluency_score) as avg_fluency,
                        AVG(confidence_score) as avg_confidence,
                        AVG(overall_score) as avg_overall,
                        COUNT(*) as exchange_count
                    FROM interview_exchanges 
                    WHERE session_id = ? AND overall_score IS NOT NULL
                """, (session_id,))
                
                stats = cursor.fetchone()
                
                if stats and stats[7] > 0:  # exchange_count > 0
                    avg_correctness = stats[0] or 0
                    avg_completeness = stats[1] or 0
                    avg_clarity = stats[2] or 0
                    avg_skill_relevance = stats[3] or 0
                    avg_fluency = stats[4] or 0
                    avg_confidence = stats[5] or 0
                    avg_overall = stats[6] or 0
                    exchange_count = stats[7]
                    
                    # Calculate technical and communication scores
                    technical_score = (avg_correctness + avg_completeness + avg_skill_relevance) / 3
                    communication_score = (avg_clarity + avg_fluency + avg_confidence) / 3
                    
                    # Update session statistics with graceful column handling
                    try:
                        conn.execute("""
                            UPDATE interview_sessions SET
                                overall_score = ?,
                                technical_score = ?,
                                communication_score = ?,
                                total_questions = ?,
                                updated_at = ?
                            WHERE session_id = ?
                        """, (
                            avg_overall,
                            technical_score,
                            communication_score,
                            exchange_count,
                            datetime.now().isoformat(),
                            session_id
                        ))
                        conn.commit()
                    except sqlite3.OperationalError as e:
                        if "no such column" in str(e):
                            # Fallback update without updated_at
                            conn.execute("""
                                UPDATE interview_sessions SET
                                    overall_score = ?,
                                    technical_score = ?,
                                    communication_score = ?,
                                    total_questions = ?
                                WHERE session_id = ?
                            """, (
                                avg_overall,
                                technical_score,
                                communication_score,
                                exchange_count,
                                session_id
                            ))
                            conn.commit()
                        else:
                            raise
                    
                    print(f"📊 AUTOMATED_EVAL: Updated session {session_id} statistics:")
                    print(f"   📈 Overall Score: {avg_overall:.1f}/10")
                    print(f"   🔧 Technical Score: {technical_score:.1f}/10")
                    print(f"   💬 Communication Score: {communication_score:.1f}/10")
                    print(f"   📝 Total Questions: {exchange_count}")
                
        except Exception as e:
            logger.error(f"❌ AUTOMATED_EVAL: Failed to update session statistics: {e}")
    
    def queue_evaluation(self, session_id, question, response, response_duration, candidate_name="Unknown", position="Unknown"):
        """Queue an evaluation for background processing"""
        evaluation_data = {
            "session_id": session_id,
            "question": question,
            "response": response,
            "response_duration": response_duration,
            "candidate_name": candidate_name,
            "position": position,
            "timestamp": datetime.now().isoformat()
        }
        
        self.evaluation_queue.put(evaluation_data)
        print(f"📤 AUTOMATED_EVAL: Queued evaluation for session {session_id}")
    
    def get_session_summary(self, session_id):
        """Get automated evaluation summary for a session"""
        try:
            with self.get_db_connection() as conn:
                # Get session info
                cursor = conn.execute("""
                    SELECT candidate_name, position, start_time, end_time, 
                           overall_score, technical_score, communication_score, total_questions
                    FROM interview_sessions WHERE session_id = ?
                """, (session_id,))
                
                session_info = cursor.fetchone()
                if not session_info:
                    return {"error": "Session not found"}
                
                # Get all exchanges with evaluations
                cursor = conn.execute("""
                    SELECT question, response, response_duration, overall_score,
                           correctness_score, completeness_score, clarity_score,
                           key_skills_demonstrated, areas_of_concern,
                           timestamp, evaluated_at
                    FROM interview_exchanges 
                    WHERE session_id = ?
                    ORDER BY timestamp
                """, (session_id,))
                
                exchanges = cursor.fetchall()
                
                return {
                    "session_id": session_id,
                    "candidate_name": session_info[0],
                    "position": session_info[1],
                    "start_time": session_info[2],
                    "end_time": session_info[3],
                    "overall_score": session_info[4] or 0,
                    "technical_score": session_info[5] or 0,
                    "communication_score": session_info[6] or 0,
                    "total_questions": session_info[7] or 0,
                    "exchanges": [
                        {
                            "question": ex[0],
                            "response": ex[1],
                            "response_duration": ex[2],
                            "overall_score": ex[3] or 0,
                            "correctness_score": ex[4] or 0,
                            "completeness_score": ex[5] or 0,
                            "clarity_score": ex[6] or 0,
                            "key_skills": json.loads(ex[7]) if ex[7] else [],
                            "concerns": json.loads(ex[8]) if ex[8] else [],
                            "timestamp": ex[9],
                            "evaluated_at": ex[10]
                        }
                        for ex in exchanges
                    ]
                }
                
        except Exception as e:
            logger.error(f"❌ AUTOMATED_EVAL: Failed to get session summary: {e}")
            return {"error": str(e)}

# Global instance
_automated_evaluator = None

def get_automated_evaluator(google_api_key=None):
    """Get the global automated evaluator instance"""
    global _automated_evaluator
    if _automated_evaluator is None:
        _automated_evaluator = AutomatedEvaluationSystem(google_api_key)
    return _automated_evaluator

def initialize_automated_evaluation(google_api_key):
    """Initialize the automated evaluation system"""
    global _automated_evaluator
    _automated_evaluator = AutomatedEvaluationSystem(google_api_key)
    return _automated_evaluator

if __name__ == "__main__":
    # Test the automated evaluation system
    print("🧪 Testing Automated Evaluation System...")
    
    import os
    google_api_key = os.getenv("GOOGLE_API_KEY")
    
    evaluator = AutomatedEvaluationSystem(google_api_key)
    
    # Test evaluation
    evaluator.queue_evaluation(
        session_id="test_session_123",
        question="Tell me about your experience with Python",
        response="I have been working with Python for 3 years, mainly developing web applications using Django and Flask frameworks. I have experience with REST APIs, database integration, and automated testing.",
        response_duration=45.0,
        candidate_name="Test Candidate",
        position="Backend Developer"
    )
    
    # Wait a bit for processing
    import time
    time.sleep(3)
    
    # Get summary
    summary = evaluator.get_session_summary("test_session_123")
    print("\n📊 Test Summary:")
    print(json.dumps(summary, indent=2))
    
    # Stop worker
    evaluator.stop_evaluation_worker()
    print("✅ Test completed!")
