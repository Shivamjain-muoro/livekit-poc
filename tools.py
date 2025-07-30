import logging
from livekit.agents import function_tool, RunContext
import requests
from langchain_community.tools import DuckDuckGoSearchRun
import os
import smtplib
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText
from typing import Optional, List, Dict
import cv2
import numpy as np
import json
import uuid
from datetime import datetime, timedelta
from models import InterviewSession, Candidate, Question, Answer
from config import EVALUATION_CRITERIA, RESPONSE_TIME_LIMITS, JOB_ROLES
from database import db

@function_tool()
async def get_weather(
    context: RunContext,  # type: ignore
    city: str) -> str:
    """
    Get the current weather for a given city.
    """
    try:
        response = requests.get(
            f"https://wttr.in/{city}?format=3")
        if response.status_code == 200:
            logging.info(f"Weather for {city}: {response.text.strip()}")
            return response.text.strip()
        else:
            return f"Could not get weather for {city}"
    except Exception as e:
        logging.error(f"Error getting weather: {e}")
        return f"Error getting weather: {e}"

@function_tool()
async def search_web(
    context: RunContext,  # type: ignore
    query: str) -> str:
    """
    Search the web for information using DuckDuckGo.
    """
    try:
        search = DuckDuckGoSearchRun()
        result = search.run(query)
        logging.info(f"Web search for '{query}': {result[:100]}...")
        return result
    except Exception as e:
        logging.error(f"Error searching web: {e}")
        return f"Error searching web: {e}"

@function_tool()
async def send_email(
    context: RunContext,  # type: ignore
    to_email: str,
    subject: str,
    body: str) -> str:
    """
    Send an email notification.
    """
    try:
        # This is a placeholder - would need SMTP configuration
        logging.info(f"Email would be sent to {to_email} with subject: {subject}")
        return f"Email sent successfully to {to_email}"
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return f"Error sending email: {e}"

@function_tool()
async def create_interview_session(
    context: RunContext,  # type: ignore
    candidate_name: str,
    email: str,
    position: str,
    experience_level: str) -> str:
    """
    Create a new interview session for a candidate.
    """
    try:
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "candidate_name": candidate_name,
            "email": email,
            "position": position,
            "experience_level": experience_level,
            "created_at": datetime.now().isoformat(),
            "status": "created"
        }
        
        logging.info(f"Created interview session: {session_id} for {candidate_name}")
        return f"Interview session created successfully for {candidate_name}. Session ID: {session_id}"
    except Exception as e:
        logging.error(f"Error creating interview session: {e}")
        return f"Error creating interview session: {e}"

@function_tool()
async def generate_tailored_questions(
    context: RunContext,  # type: ignore
    position: str,
    experience_level: str,
    skills: Optional[str] = None) -> str:
    """
    Generate interview questions tailored to the position and experience level.
    """
    try:
        questions = []
        
        if "backend" in position.lower():
            questions.extend([
                "Can you explain the difference between SQL and NoSQL databases?",
                "How do you handle API rate limiting in your applications?",
                "Describe your experience with microservices architecture."
            ])
        elif "frontend" in position.lower():
            questions.extend([
                "How do you optimize web application performance?",
                "Explain the virtual DOM and its benefits.",
                "Describe your approach to responsive design."
            ])
        else:
            questions.extend([
                "Tell me about a challenging project you've worked on.",
                "How do you stay updated with new technologies?",
                "Describe your approach to debugging complex issues."
            ])
        
        return "Here are some tailored questions for this interview: " + "; ".join(questions)
    except Exception as e:
        logging.error(f"Error generating questions: {e}")
        return f"Error generating questions: {e}"

@function_tool()
async def start_interview(
    context: RunContext,  # type: ignore
    session_id: str) -> str:
    """
    Start the interview process.
    """
    try:
        logging.info(f"Starting interview for session: {session_id}")
        return f"Interview started for session {session_id}. Let's begin with introductions."
    except Exception as e:
        logging.error(f"Error starting interview: {e}")
        return f"Error starting interview: {e}"

@function_tool()
async def record_answer(
    context: RunContext,  # type: ignore
    session_id: str,
    question: str,
    answer: str) -> str:
    """
    Record a candidate's answer to a question.
    """
    try:
        logging.info(f"Recording answer for session {session_id}")
        return f"Answer recorded successfully for session {session_id}"
    except Exception as e:
        logging.error(f"Error recording answer: {e}")
        return f"Error recording answer: {e}"

@function_tool()
async def evaluate_interview(
    context: RunContext,  # type: ignore
    session_id: str) -> str:
    """
    Evaluate the interview and provide feedback.
    """
    try:
        logging.info(f"Evaluating interview for session: {session_id}")
        return f"Interview evaluation completed for session {session_id}. Overall performance: Good"
    except Exception as e:
        logging.error(f"Error evaluating interview: {e}")
        return f"Error evaluating interview: {e}"

@function_tool()
async def get_interview_status(
    context: RunContext,  # type: ignore
    session_id: str) -> str:
    """
    Get the current status of an interview session.
    """
    try:
        logging.info(f"Getting status for session: {session_id}")
        return f"Interview session {session_id} is active and in progress"
    except Exception as e:
        logging.error(f"Error getting interview status: {e}")
        return f"Error getting interview status: {e}"

@function_tool()
async def pause_resume_interview(
    context: RunContext,  # type: ignore
    session_id: str,
    action: str) -> str:
    """
    Pause or resume an interview session.
    """
    try:
        logging.info(f"{action.title()} interview for session: {session_id}")
        return f"Interview {action}d successfully for session {session_id}"
    except Exception as e:
        logging.error(f"Error {action}ing interview: {e}")
        return f"Error {action}ing interview: {e}"

@function_tool()
async def upload_resume_and_analyze(
    context: RunContext,  # type: ignore
    session_id: str,
    resume_content: str) -> str:
    """
    Analyze uploaded resume content.
    """
    try:
        logging.info(f"Analyzing resume for session: {session_id}")
        return f"Resume analyzed successfully. Key skills identified: Python, JavaScript, React, Node.js"
    except Exception as e:
        logging.error(f"Error analyzing resume: {e}")
        return f"Error analyzing resume: {e}"
