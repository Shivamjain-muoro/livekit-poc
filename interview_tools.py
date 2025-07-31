"""
Pure LiveKit Interview Tools
Following the exact pattern from Friday/Jarvis repo
"""

import logging
from livekit.agents import function_tool, RunContext
from typing import List, Dict, Optional
import json
import google.generativeai as genai
import os
from datetime import datetime

# Configure Google AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

@function_tool()
async def generate_interview_questions(
    context: RunContext,
    candidate_name: str,
    position: str,
    experience_level: str,
    skills: str
) -> str:
    """
    Generate personalized interview questions based on candidate profile.
    
    Args:
        candidate_name: Name of the candidate
        position: Job position they're applying for
        experience_level: Their experience level (entry, mid, senior)
        skills: Comma-separated list of their skills
    """
    logging.info("🎯 FUNCTION CALL: generate_interview_questions")
    logging.info(f"   📝 Parameters: name='{candidate_name}', position='{position}', level='{experience_level}', skills='{skills}'")
    
    try:
        if GOOGLE_API_KEY:
            logging.info("   🤖 Using Google AI to generate questions")
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""Generate 5 excellent interview questions for a {position} position.

Candidate Profile:
- Name: {candidate_name}
- Position: {position}
- Experience Level: {experience_level}
- Skills: {skills}

Requirements:
- Mix of behavioral, technical, and situational questions
- Personalized to their experience level and skills
- Conversational and engaging tone
- Allow for detailed responses (1-2 minutes each)

Return as a JSON array of questions."""
            
            logging.info("   📤 Sending request to Google AI...")
            response = model.generate_content(prompt)
            questions_text = response.text.strip()
            logging.info(f"   📥 Received response: {len(questions_text)} characters")
            
            # Extract questions from response
            if '[' in questions_text and ']' in questions_text:
                start = questions_text.find('[')
                end = questions_text.rfind(']') + 1
                questions_json = questions_text[start:end]
                questions = json.loads(questions_json)
                logging.info(f"   ✅ Successfully parsed {len(questions)} questions from JSON")
            else:
                # Fallback: split by lines
                questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
                logging.info(f"   ⚠️ Used fallback parsing, got {len(questions)} questions")
            
            logging.info(f"✅ Generated {len(questions)} questions for {candidate_name}")
            result = json.dumps(questions)
            logging.info(f"   📋 Returning questions: {result[:200]}...")
            return result
        
        else:
            logging.info("   ⚠️ No Google API key found, using fallback questions")
            # Fallback questions
            fallback_questions = [
                f"Tell me about yourself and what interests you most about the {position} role.",
                f"With your {experience_level} level experience, describe a challenging project you're particularly proud of.",
                "Tell me about a time when you had to work through a difficult problem with a team.",
                f"Looking at your skills in {skills}, can you give me a specific example of how you've applied these?",
                f"Where do you see yourself growing in your {position} career over the next few years?"
            ]
            
            logging.info(f"✅ Using fallback questions for {candidate_name}")
            result = json.dumps(fallback_questions)
            logging.info(f"   📋 Returning fallback questions: {len(fallback_questions)} items")
            return result
            
    except Exception as e:
        logging.error(f"❌ ERROR in generate_interview_questions: {e}")
        logging.error(f"   📊 Error type: {type(e).__name__}")
        logging.error(f"   📝 Parameters were: name='{candidate_name}', position='{position}', level='{experience_level}', skills='{skills}'")
        
        fallback_result = json.dumps([
            "Tell me about your background and experience.",
            "What interests you most about this role?",
            "Describe a challenging project you've worked on.",
            "How do you handle working in a team?",
            "What are your career goals?"
        ])
        logging.info(f"   🔄 Returning error fallback questions")
        return fallback_result

@function_tool()
async def evaluate_candidate_response(
    context: RunContext,
    question: str,
    candidate_response: str,
    evaluation_criteria: str = "communication,technical_knowledge,problem_solving"
) -> str:
    """
    Evaluate a candidate's response to an interview question.
    
    Args:
        question: The interview question that was asked
        candidate_response: The candidate's response
        evaluation_criteria: Criteria to evaluate (comma-separated)
    """
    logging.info("🎯 FUNCTION CALL: evaluate_candidate_response")
    logging.info(f"   ❓ Question: {question[:100]}...")
    logging.info(f"   💬 Response length: {len(candidate_response)} characters")
    logging.info(f"   📊 Criteria: {evaluation_criteria}")
    logging.info(f"   💭 Response preview: {candidate_response[:150]}...")
    
    try:
        if GOOGLE_API_KEY and candidate_response.strip():
            logging.info("   🤖 Using Google AI for evaluation")
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""Evaluate this interview response:

Question: {question}
Candidate Response: {candidate_response}
Evaluation Criteria: {evaluation_criteria}

Provide:
1. Brief positive feedback (1-2 sentences)
2. Score out of 10 for each criteria
3. One follow-up question if appropriate

Format as JSON with keys: feedback, scores, follow_up_question"""
            
            logging.info("   📤 Sending evaluation request to Google AI...")
            response = model.generate_content(prompt)
            evaluation = response.text.strip()
            logging.info(f"   📥 Received evaluation: {len(evaluation)} characters")
            logging.info(f"   📝 Evaluation preview: {evaluation[:200]}...")
            
            logging.info(f"✅ Evaluated response - Question: {question[:50]}...")
            return evaluation
            
        else:
            if not GOOGLE_API_KEY:
                logging.warning("   ⚠️ No Google API key found, using fallback evaluation")
            if not candidate_response.strip():
                logging.warning("   ⚠️ Empty candidate response, using fallback evaluation")
                
            # Simple fallback evaluation
            fallback_eval = {
                "feedback": "Thank you for sharing that insight. That's a great example of your experience.",
                "scores": {"communication": 8, "relevance": 7},
                "follow_up_question": "Can you tell me more about the challenges you faced in that situation?"
            }
            
            logging.info("✅ Using fallback evaluation")
            result = json.dumps(fallback_eval)
            logging.info(f"   📋 Returning fallback evaluation: {result}")
            return result
            
    except Exception as e:
        logging.error(f"❌ ERROR in evaluate_candidate_response: {e}")
        logging.error(f"   📊 Error type: {type(e).__name__}")
        logging.error(f"   📝 Parameters were: question='{question[:50]}...', response_len={len(candidate_response)}, criteria='{evaluation_criteria}'")
        
        error_fallback = json.dumps({
            "feedback": "Thank you for that response.",
            "scores": {"overall": 7},
            "follow_up_question": None
        })
        logging.info(f"   🔄 Returning error fallback evaluation")
        return error_fallback

@function_tool()
async def get_candidate_profile(
    context: RunContext,
    session_id: str
) -> str:
    """
    Retrieve candidate profile information for the interview session.
    
    Args:
        session_id: The interview session identifier
    """
    logging.info("🎯 FUNCTION CALL: get_candidate_profile")
    logging.info(f"   🆔 Session ID: {session_id}")
    
    try:
        # Full implementation: Try to fetch from database first
        import sqlite3
        db_path = "interview_sessions.db"
        logging.info(f"   💾 Database path: {db_path}")
        
        # Initialize database if it doesn't exist
        logging.info("   🔗 Connecting to database...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        logging.info("   ✅ Database connection established")
        
        # Create table if not exists
        logging.info("   🏗️ Creating candidate_profiles table if not exists...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidate_profiles (
                session_id TEXT PRIMARY KEY,
                name TEXT,
                position TEXT,
                experience_level TEXT,
                skills TEXT,
                interview_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logging.info("   ✅ Table creation/verification completed")
        
        # Try to fetch existing profile
        logging.info(f"   🔍 Searching for existing profile with session_id: {session_id}")
        cursor.execute("SELECT * FROM candidate_profiles WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        
        if row:
            # Profile exists in database
            logging.info("   ✅ Found existing profile in database")
            logging.info(f"   📝 Profile data: name='{row[1]}', position='{row[2]}', experience='{row[3]}'")
            
            profile = {
                "session_id": row[0],
                "name": row[1],
                "position": row[2],
                "experience_level": row[3],
                "skills": row[4],
                "interview_type": row[5],
                "created_at": row[6]
            }
            conn.close()
            logging.info(f"✅ Retrieved existing profile for session: {session_id}")
            result = json.dumps(profile)
            logging.info(f"   📋 Returning profile: {result}")
            return result
        else:
            # Create new profile with reasonable defaults
            logging.info("   ⚠️ No existing profile found, creating new profile")
            new_profile = {
                "name": "Interview Candidate",
                "position": "Software Developer",
                "experience_level": "mid",
                "skills": "Python, JavaScript, React, Node.js",
                "session_id": session_id,
                "interview_type": "technical"
            }
            logging.info(f"   📝 New profile data: {new_profile}")
            
            # Insert new profile
            logging.info("   💾 Inserting new profile into database...")
            cursor.execute('''
                INSERT INTO candidate_profiles 
                (session_id, name, position, experience_level, skills, interview_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, new_profile["name"], new_profile["position"], 
                  new_profile["experience_level"], new_profile["skills"], 
                  new_profile["interview_type"]))
            
            conn.commit()
            logging.info("   ✅ Database commit successful")
            conn.close()
            logging.info("   🔒 Database connection closed")
            
            logging.info(f"✅ Created new profile for session: {session_id}")
            result = json.dumps(new_profile)
            logging.info(f"   📋 Returning new profile: {result}")
            return result
        
    except Exception as e:
        logging.error(f"❌ ERROR in get_candidate_profile: {e}")
        logging.error(f"   📊 Error type: {type(e).__name__}")
        logging.error(f"   🆔 Session ID was: {session_id}")
        
        # Fallback to default profile
        fallback_profile = {
            "name": "Interview Candidate",
            "position": "Software Developer", 
            "experience_level": "mid",
            "skills": "General programming skills",
            "session_id": session_id,
            "interview_type": "general"
        }
        logging.info(f"   🔄 Returning error fallback profile")
        return json.dumps(fallback_profile)

@function_tool()
async def save_interview_response(
    context: RunContext,
    session_id: str,
    question: str,
    response: str,
    evaluation: str
) -> str:
    """
    Save candidate response and evaluation to interview record.
    
    Args:
        session_id: Interview session ID
        question: The question that was asked
        response: Candidate's response
        evaluation: AI evaluation of the response
    """
    logging.info("🎯 FUNCTION CALL: save_interview_response")
    logging.info(f"   🆔 Session ID: {session_id}")
    logging.info(f"   ❓ Question length: {len(question)} characters")
    logging.info(f"   💬 Response length: {len(response)} characters")
    logging.info(f"   ⭐ Evaluation length: {len(evaluation)} characters")
    logging.info(f"   📝 Question preview: {question[:100]}...")
    logging.info(f"   💭 Response preview: {response[:150]}...")
    logging.info(f"   📊 Evaluation preview: {evaluation[:150]}...")
    
    try:
        # Full implementation: Save to database
        import sqlite3
        db_path = "interview_sessions.db"
        logging.info(f"   💾 Database path: {db_path}")
        
        logging.info("   🔗 Connecting to database...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        logging.info("   ✅ Database connection established")
        
        # Create table if not exists
        logging.info("   🏗️ Creating interview_responses table if not exists...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                question TEXT,
                response TEXT,
                evaluation TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES candidate_profiles (session_id)
            )
        ''')
        logging.info("   ✅ Table creation/verification completed")
        
        # Insert the interview response
        logging.info("   💾 Inserting interview response into database...")
        cursor.execute('''
            INSERT INTO interview_responses 
            (session_id, question, response, evaluation) 
            VALUES (?, ?, ?, ?)
        ''', (session_id, question, response, evaluation))
        
        response_id = cursor.lastrowid
        logging.info(f"   ✅ Inserted with response ID: {response_id}")
        
        conn.commit()
        logging.info("   ✅ Database commit successful")
        conn.close()
        logging.info("   🔒 Database connection closed")
        
        logging.info(f"✅ Saved interview response #{response_id} for session: {session_id}")
        logging.debug(f"   📝 Question: {question[:100]}...")
        logging.debug(f"   💬 Response: {response[:100]}...")
        
        result_message = f"Response saved successfully with ID: {response_id}"
        logging.info(f"   📋 Returning success message: {result_message}")
        return result_message
        
    except Exception as e:
        logging.error(f"❌ ERROR in save_interview_response: {e}")
        logging.error(f"   📊 Error type: {type(e).__name__}")
        logging.error(f"   🆔 Session ID was: {session_id}")
        logging.error(f"   📝 Data lengths: question={len(question)}, response={len(response)}, evaluation={len(evaluation)}")
        
        error_message = f"Error saving response: {str(e)}"
        logging.error(f"   🔄 Returning error message: {error_message}")
        return error_message

@function_tool()
async def complete_interview_session(
    context: RunContext,
    session_id: str,
    overall_assessment: str
) -> str:
    """
    Complete the interview session with final assessment.
    
    Args:
        session_id: Interview session ID
        overall_assessment: Final assessment of the candidate
    """
    logging.info("🎯 FUNCTION CALL: complete_interview_session")
    logging.info(f"   🆔 Session ID: {session_id}")
    logging.info(f"   📊 Assessment length: {len(overall_assessment)} characters")
    logging.info(f"   📝 Assessment preview: {overall_assessment[:200]}...")
    
    try:
        # Full implementation: Save to database
        import sqlite3
        db_path = "interview_sessions.db"
        logging.info(f"   💾 Database path: {db_path}")
        
        logging.info("   🔗 Connecting to database...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        logging.info("   ✅ Database connection established")
        
        # Create table if not exists
        logging.info("   🏗️ Creating interview_sessions table if not exists...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_sessions (
                session_id TEXT PRIMARY KEY,
                overall_assessment TEXT,
                status TEXT,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_responses INTEGER,
                FOREIGN KEY (session_id) REFERENCES candidate_profiles (session_id)
            )
        ''')
        logging.info("   ✅ Table creation/verification completed")
        
        # Count total responses for this session
        logging.info(f"   🔢 Counting responses for session: {session_id}")
        cursor.execute(
            "SELECT COUNT(*) FROM interview_responses WHERE session_id = ?", 
            (session_id,)
        )
        total_responses = cursor.fetchone()[0]
        logging.info(f"   📊 Found {total_responses} responses for this session")
        
        # Insert or update completion data
        logging.info("   💾 Inserting/updating session completion data...")
        cursor.execute('''
            INSERT OR REPLACE INTO interview_sessions 
            (session_id, overall_assessment, status, total_responses) 
            VALUES (?, ?, ?, ?)
        ''', (session_id, overall_assessment, "completed", total_responses))
        
        conn.commit()
        logging.info("   ✅ Database commit successful")
        conn.close()
        logging.info("   🔒 Database connection closed")
        
        logging.info(f"✅ Completed interview session: {session_id}")
        logging.info(f"   📊 Total responses recorded: {total_responses}")
        logging.info(f"   📝 Final assessment: {overall_assessment[:200]}...")
        
        result_message = f"Interview session completed successfully. {total_responses} responses recorded."
        logging.info(f"   📋 Returning success message: {result_message}")
        return result_message
        
    except Exception as e:
        logging.error(f"❌ ERROR in complete_interview_session: {e}")
        logging.error(f"   📊 Error type: {type(e).__name__}")
        logging.error(f"   🆔 Session ID was: {session_id}")
        logging.error(f"   📝 Assessment length was: {len(overall_assessment)}")
        
        error_message = f"Error completing session: {str(e)}"
        logging.error(f"   🔄 Returning error message: {error_message}")
        return error_message

@function_tool()
async def get_interview_feedback(
    context: RunContext,
    session_id: str
) -> str:
    """
    Retrieve comprehensive feedback and summary for a completed interview.
    
    Args:
        session_id: Interview session ID
    """
    logging.info("🎯 FUNCTION CALL: get_interview_feedback")
    logging.info(f"   🆔 Session ID: {session_id}")
    
    try:
        import sqlite3
        db_path = "interview_sessions.db"
        logging.info(f"   💾 Database path: {db_path}")
        
        logging.info("   🔗 Connecting to database...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        logging.info("   ✅ Database connection established")
        
        # Get session completion info
        logging.info("   🔍 Fetching session completion info...")
        cursor.execute("""
            SELECT overall_assessment, status, completed_at, total_responses 
            FROM interview_sessions 
            WHERE session_id = ?
        """, (session_id,))
        session_row = cursor.fetchone()
        
        if not session_row:
            logging.warning(f"   ⚠️ No session completion data found for session: {session_id}")
            conn.close()
            error_result = json.dumps({"error": "Interview session not found or not completed"})
            logging.info(f"   📋 Returning error: {error_result}")
            return error_result
        
        logging.info(f"   ✅ Found session data: status='{session_row[1]}', responses={session_row[3]}")
        
        # Get candidate profile
        logging.info("   🔍 Fetching candidate profile...")
        cursor.execute("SELECT name, position, experience_level FROM candidate_profiles WHERE session_id = ?", (session_id,))
        profile_row = cursor.fetchone()
        
        if profile_row:
            logging.info(f"   ✅ Found profile: name='{profile_row[0]}', position='{profile_row[1]}', level='{profile_row[2]}'")
        else:
            logging.warning(f"   ⚠️ No profile found for session: {session_id}")
        
        # Get all responses and evaluations
        logging.info("   🔍 Fetching all responses and evaluations...")
        cursor.execute("""
            SELECT question, response, evaluation, timestamp 
            FROM interview_responses 
            WHERE session_id = ? 
            ORDER BY timestamp
        """, (session_id,))
        responses = cursor.fetchall()
        
        logging.info(f"   ✅ Found {len(responses)} responses")
        conn.close()
        logging.info("   🔒 Database connection closed")
        
        # Build comprehensive feedback
        logging.info("   🏗️ Building comprehensive feedback summary...")
        feedback_summary = {
            "session_id": session_id,
            "candidate_name": profile_row[0] if profile_row else "Unknown",
            "position": profile_row[1] if profile_row else "Unknown",
            "experience_level": profile_row[2] if profile_row else "Unknown",
            "interview_status": session_row[1],
            "completed_at": session_row[2],
            "total_questions": session_row[3],
            "overall_assessment": session_row[0],
            "detailed_responses": []
        }
        
        for i, (question, response, evaluation, timestamp) in enumerate(responses, 1):
            feedback_summary["detailed_responses"].append({
                "question_number": i,
                "question": question,
                "candidate_response": response[:200] + "..." if len(response) > 200 else response,
                "evaluation": evaluation,
                "timestamp": timestamp
            })
        
        logging.info(f"✅ Generated comprehensive feedback for session: {session_id}")
        result = json.dumps(feedback_summary, indent=2)
        logging.info(f"   📋 Returning feedback summary: {len(result)} characters")
        return result
        
    except Exception as e:
        logging.error(f"❌ ERROR in get_interview_feedback: {e}")
        logging.error(f"   📊 Error type: {type(e).__name__}")
        logging.error(f"   🆔 Session ID was: {session_id}")
        
        error_result = json.dumps({"error": f"Failed to retrieve feedback: {str(e)}"})
        logging.error(f"   🔄 Returning error result: {error_result}")
        return error_result

@function_tool()
async def generate_interview_report(
    context: RunContext,
    session_id: str
) -> str:
    """
    Generate a professional interview report with AI analysis.
    
    Args:
        session_id: Interview session ID
    """
    logging.info("🎯 FUNCTION CALL: generate_interview_report")
    logging.info(f"   🆔 Session ID: {session_id}")
    
    try:
        # Get the comprehensive feedback first
        logging.info("   📊 Getting comprehensive feedback first...")
        feedback_json = await get_interview_feedback(context, session_id)
        feedback_data = json.loads(feedback_json)
        
        if "error" in feedback_data:
            logging.warning(f"   ⚠️ Error in feedback data: {feedback_data['error']}")
            return feedback_json
        
        logging.info(f"   ✅ Retrieved feedback data for: {feedback_data['candidate_name']}")
        
        # Use Google AI to generate a professional report
        if GOOGLE_API_KEY:
            logging.info("   🤖 Using Google AI to generate professional report...")
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""Generate a professional interview report based on this data:

Candidate: {feedback_data['candidate_name']}
Position: {feedback_data['position']} 
Experience Level: {feedback_data['experience_level']}
Total Questions: {feedback_data['total_questions']}
Overall Assessment: {feedback_data['overall_assessment']}

Detailed Response Analysis:
{json.dumps(feedback_data['detailed_responses'], indent=2)}

Please provide:
1. Executive Summary (2-3 sentences)
2. Key Strengths (3-4 bullet points)  
3. Areas for Improvement (2-3 bullet points)
4. Overall Recommendation (Hire/No Hire/Further Interview)
5. Confidence Score (1-10)

Format as a professional report."""
            
            logging.info("   📤 Sending report generation request to Google AI...")
            response = model.generate_content(prompt)
            report = response.text.strip()
            logging.info(f"   📥 Received AI report: {len(report)} characters")
            
            logging.info(f"✅ Generated AI interview report for session: {session_id}")
            logging.info(f"   📋 Report preview: {report[:200]}...")
            return report
        else:
            logging.warning("   ⚠️ No Google API key found, using basic fallback report")
            # Fallback basic report
            basic_report = f"""
INTERVIEW REPORT
================
Candidate: {feedback_data['candidate_name']}
Position: {feedback_data['position']}
Questions Answered: {feedback_data['total_questions']}
Status: {feedback_data['interview_status']}

Overall Assessment: {feedback_data['overall_assessment']}

For detailed evaluation, please review individual response scores.
            """
            result = basic_report.strip()
            logging.info(f"   📋 Returning basic report: {len(result)} characters")
            return result
            
    except Exception as e:
        logging.error(f"❌ ERROR in generate_interview_report: {e}")
        logging.error(f"   📊 Error type: {type(e).__name__}")
        logging.error(f"   🆔 Session ID was: {session_id}")
        
        error_message = f"Error generating report: {str(e)}"
        logging.error(f"   🔄 Returning error message: {error_message}")
        return error_message
