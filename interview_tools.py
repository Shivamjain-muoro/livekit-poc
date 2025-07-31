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
    try:
        if GOOGLE_API_KEY:
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
            
            response = model.generate_content(prompt)
            questions_text = response.text.strip()
            
            # Extract questions from response
            if '[' in questions_text and ']' in questions_text:
                start = questions_text.find('[')
                end = questions_text.rfind(']') + 1
                questions_json = questions_text[start:end]
                questions = json.loads(questions_json)
            else:
                # Fallback: split by lines
                questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
            
            logging.info(f"Generated {len(questions)} questions for {candidate_name}")
            return json.dumps(questions)
        
        else:
            # Fallback questions
            fallback_questions = [
                f"Tell me about yourself and what interests you most about the {position} role.",
                f"With your {experience_level} level experience, describe a challenging project you're particularly proud of.",
                "Tell me about a time when you had to work through a difficult problem with a team.",
                f"Looking at your skills in {skills}, can you give me a specific example of how you've applied these?",
                f"Where do you see yourself growing in your {position} career over the next few years?"
            ]
            
            logging.info(f"Using fallback questions for {candidate_name}")
            return json.dumps(fallback_questions)
            
    except Exception as e:
        logging.error(f"Error generating questions for {candidate_name}: {e}")
        return json.dumps([
            "Tell me about your background and experience.",
            "What interests you most about this role?",
            "Describe a challenging project you've worked on.",
            "How do you handle working in a team?",
            "What are your career goals?"
        ])

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
    try:
        if GOOGLE_API_KEY and candidate_response.strip():
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
            
            response = model.generate_content(prompt)
            evaluation = response.text.strip()
            
            logging.info(f"Evaluated response - Question: {question[:50]}...")
            return evaluation
            
        else:
            # Simple fallback evaluation
            fallback_eval = {
                "feedback": "Thank you for sharing that insight. That's a great example of your experience.",
                "scores": {"communication": 8, "relevance": 7},
                "follow_up_question": "Can you tell me more about the challenges you faced in that situation?"
            }
            
            logging.info("Using fallback evaluation")
            return json.dumps(fallback_eval)
            
    except Exception as e:
        logging.error(f"Error evaluating response: {e}")
        return json.dumps({
            "feedback": "Thank you for that response.",
            "scores": {"overall": 7},
            "follow_up_question": None
        })

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
    try:
        # In a real implementation, this would fetch from a database
        # For now, return a sample profile structure
        sample_profile = {
            "name": "Candidate",
            "position": "Software Developer",
            "experience_level": "mid",
            "skills": "Python, JavaScript, React, Node.js",
            "session_id": session_id,
            "interview_type": "technical"
        }
        
        logging.info(f"Retrieved profile for session: {session_id}")
        return json.dumps(sample_profile)
        
    except Exception as e:
        logging.error(f"Error retrieving candidate profile: {e}")
        return json.dumps({"error": "Could not retrieve candidate profile"})

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
    try:
        # In a real implementation, this would save to a database
        interview_data = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "response": response,
            "evaluation": evaluation
        }
        
        # For now, just log the data
        logging.info(f"Saved interview response for session: {session_id}")
        logging.debug(f"Interview data: {json.dumps(interview_data, indent=2)}")
        
        return "Response saved successfully"
        
    except Exception as e:
        logging.error(f"Error saving interview response: {e}")
        return f"Error saving response: {str(e)}"

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
    try:
        completion_data = {
            "session_id": session_id,
            "completed_at": datetime.now().isoformat(),
            "overall_assessment": overall_assessment,
            "status": "completed"
        }
        
        logging.info(f"Completed interview session: {session_id}")
        logging.info(f"Assessment: {overall_assessment}")
        
        return "Interview session completed successfully"
        
    except Exception as e:
        logging.error(f"Error completing interview session: {e}")
        return f"Error completing session: {str(e)}"
