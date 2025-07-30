"""
Enhanced AI Interview Agent with Google Gemini Integration
=========================================================
This agent integrates with our FastAPI backend and provides a complete
LiveKit-based interview experience using Google Gemini for LLM capabilities.
"""

import asyncio
import logging
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Optional

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, function_tool, RunContext
from livekit.plugins import noise_cancellation, google
import aiohttp

from prompts import SESSION_INSTRUCTION, INTERVIEWER_INSTRUCTION

load_dotenv()

# Backend API configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8002")

# Session state management
session_states: Dict[str, Dict] = {}

@function_tool()
async def create_interview_session(
    context: RunContext,
    candidate_name: str,
    email: str,
    position: str,
    experience_level: str
) -> str:
    """Create a new interview session for a candidate."""
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "candidate": {
                    "name": candidate_name,
                    "email": email,
                    "position": position,
                    "experience_level": experience_level,
                    "skills": []
                },
                "interview_type": "technical"
            }
            
            async with session.post(f"{BACKEND_URL}/api/interview/create", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    session_id = data["session_id"]
                    
                    # Store session state
                    room_name = context.room.name
                    session_states[room_name] = {
                        "session_id": session_id,
                        "candidate_name": candidate_name,
                        "position": position,
                        "status": "created",
                        "current_question": None,
                        "questions_answered": 0
                    }
                    
                    logging.info(f"Created interview session: {session_id} for {candidate_name}")
                    return f"Interview session created successfully for {candidate_name}! Session ID: {session_id}. You can now start the interview."
                else:
                    error_detail = await response.text()
                    return f"Failed to create session: {error_detail}"
                    
    except Exception as e:
        logging.error(f"Error creating interview session: {e}")
        return f"Error creating interview session: {str(e)}"

@function_tool()
async def start_interview(
    context: RunContext,
) -> str:
    """Start the interview and get the first question."""
    try:
        room_name = context.room.name
        if room_name not in session_states:
            return "No interview session found. Please create a session first."
        
        session_id = session_states[room_name]["session_id"]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BACKEND_URL}/api/interview/start/{session_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    first_question = data["first_question"]
                    
                    # Update session state
                    session_states[room_name]["status"] = "in_progress"
                    session_states[room_name]["current_question"] = first_question
                    session_states[room_name]["total_questions"] = data["total_questions"]
                    
                    question_text = first_question["question_text"]
                    question_type = first_question["question_type"]
                    estimated_time = first_question["expected_duration"] // 60
                    
                    logging.info(f"Started interview for session {session_id}")
                    return f"Interview started! Here's your first question:\n\n**{question_type.title()} Question (Estimated time: {estimated_time} minutes):**\n{question_text}\n\nPlease provide your answer when you're ready."
                else:
                    error_detail = await response.text()
                    return f"Failed to start interview: {error_detail}"
                    
    except Exception as e:
        logging.error(f"Error starting interview: {e}")
        return f"Error starting interview: {str(e)}"

@function_tool()
async def submit_answer(
    context: RunContext,
    answer_text: str,
    duration_seconds: Optional[int] = 120
) -> str:
    """Submit an answer and get evaluation plus the next question."""
    try:
        room_name = context.room.name
        if room_name not in session_states:
            return "No active interview session found."
        
        session_data = session_states[room_name]
        session_id = session_data["session_id"]
        current_question = session_data.get("current_question")
        
        if not current_question:
            return "No current question to answer. Please start the interview first."
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "session_id": session_id,
                "question_id": current_question["id"],
                "answer_text": answer_text,
                "duration": duration_seconds
            }
            
            async with session.post(f"{BACKEND_URL}/api/interview/answer/{session_id}", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    feedback = data["feedback"]
                    
                    # Update session state
                    session_states[room_name]["questions_answered"] += 1
                    
                    result = f"**Answer Evaluation:**\n"
                    result += f"Score: {feedback['score']}/5\n"
                    result += f"Feedback: {feedback['feedback_text']}\n\n"
                    
                    if feedback['strengths']:
                        result += f"**Strengths:** {', '.join(feedback['strengths'])}\n"
                    if feedback['improvements']:
                        result += f"**Areas for improvement:** {', '.join(feedback['improvements'])}\n\n"
                    
                    if data["is_complete"]:
                        # Interview complete
                        session_states[room_name]["status"] = "completed"
                        summary = data["session_summary"]
                        
                        result += f"🎉 **Interview Complete!**\n\n"
                        result += f"**Final Score:** {summary['overall_score']}/5\n"
                        result += f"**Recommendation:** {summary['recommendation'].upper()}\n"
                        result += f"**Questions Answered:** {summary['questions_asked']}\n\n"
                        
                        if summary['strengths']:
                            result += f"**Key Strengths:** {', '.join(summary['strengths'][:3])}\n"
                        if summary['areas_for_improvement']:
                            result += f"**Growth Areas:** {', '.join(summary['areas_for_improvement'][:3])}\n"
                        
                        result += f"\nThank you for completing the interview! The hiring team will review your responses."
                        
                    else:
                        # Next question
                        next_question = data["next_question"]
                        session_states[room_name]["current_question"] = next_question
                        
                        question_text = next_question["question_text"]
                        question_type = next_question["question_type"]
                        estimated_time = next_question["expected_duration"] // 60
                        current_q = session_states[room_name]["questions_answered"] + 1
                        total_q = session_states[room_name]["total_questions"]
                        
                        result += f"**Next Question ({current_q}/{total_q}) - {question_type.title()} (Est. {estimated_time} min):**\n"
                        result += f"{question_text}\n\nPlease provide your answer when you're ready."
                    
                    logging.info(f"Answer submitted for session {session_id}, score: {feedback['score']}")
                    return result
                    
                else:
                    error_detail = await response.text()
                    return f"Failed to submit answer: {error_detail}"
                    
    except Exception as e:
        logging.error(f"Error submitting answer: {e}")
        return f"Error submitting answer: {str(e)}"

@function_tool()
async def get_interview_status(
    context: RunContext,
) -> str:
    """Get the current interview status and progress."""
    try:
        room_name = context.room.name
        if room_name not in session_states:
            return "No interview session found in this room."
        
        session_data = session_states[room_name]
        session_id = session_data["session_id"]
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BACKEND_URL}/api/interview/session/{session_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    progress = data["progress"]
                    
                    status = f"**Interview Status for {session_data['candidate_name']}:**\n"
                    status += f"Position: {session_data['position']}\n"
                    status += f"Status: {session_data['status'].title()}\n"
                    status += f"Progress: {progress['current_question']}/{progress['total_questions']} questions\n"
                    status += f"Completion: {progress['percentage']:.1f}%\n"
                    
                    if session_data.get("current_question"):
                        current_q = session_data["current_question"]
                        status += f"\n**Current Question:** {current_q['question_type'].title()}\n"
                        status += f"{current_q['question_text']}"
                    
                    return status
                else:
                    return f"Failed to get interview status: {await response.text()}"
                    
    except Exception as e:
        logging.error(f"Error getting interview status: {e}")
        return f"Error getting interview status: {str(e)}"

@function_tool()
async def pause_interview(
    context: RunContext,
) -> str:
    """Pause the current interview."""
    room_name = context.room.name
    if room_name in session_states:
        session_states[room_name]["status"] = "paused"
        return "Interview paused. You can resume whenever you're ready by continuing with your answer or asking for the current question."
    return "No active interview to pause."

@function_tool()
async def resume_interview(
    context: RunContext,
) -> str:
    """Resume a paused interview."""
    room_name = context.room.name
    if room_name in session_states and session_states[room_name]["status"] == "paused":
        session_states[room_name]["status"] = "in_progress"
        current_question = session_states[room_name].get("current_question")
        if current_question:
            return f"Interview resumed! Here's your current question:\n\n{current_question['question_text']}"
        else:
            return "Interview resumed! Please use the start_interview function to begin."
    return "No paused interview found to resume."

@function_tool()
async def get_help(
    context: RunContext,
) -> str:
    """Get help and instructions for the interview process."""
    return """
**AI Interview System Help:**

**Available Commands:**
1. **Create Session**: Provide your name, email, position, and experience level
2. **Start Interview**: Begin the interview and get your first question
3. **Submit Answer**: Provide your answer to the current question
4. **Get Status**: Check your interview progress
5. **Pause/Resume**: Pause and resume the interview as needed

**Interview Flow:**
1. Start by creating your interview session
2. Begin the interview to receive your first question
3. Answer each question thoughtfully
4. Receive immediate feedback and your next question
5. Complete all questions to get your final evaluation

**Tips:**
- Take your time to provide detailed, thoughtful answers
- Ask for clarification if you don't understand a question
- You can pause the interview if you need a break
- The AI evaluates based on technical accuracy, communication, and relevance

Ready to start your interview? Just let me know your details!
"""

class InterviewAgent(Agent):
    """Enhanced Interview Agent with Google Gemini and comprehensive tools."""
    
    def __init__(self) -> None:
        super().__init__(
            instructions=SESSION_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                voice="Aoede",
                temperature=0.7,
            ),
            tools=[
                create_interview_session,
                start_interview,
                submit_answer,
                get_interview_status,
                pause_interview,
                resume_interview,
                get_help
            ],
        )

async def entrypoint(ctx: agents.JobContext):
    """Main entry point for the interview agent."""
    logging.info(f"Starting interview agent in room: {ctx.room.name}")
    
    session = AgentSession()

    await session.start(
        room=ctx.room,
        agent=InterviewAgent(),
        room_input_options=RoomInputOptions(
            auto_subscribe=True,
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()
    
    # Initial greeting
    await session.generate_reply(
        instructions="""Welcome to the AI Interview System! I'm Friday, your AI interviewer. 

I'll guide you through a comprehensive interview process that includes:
- Creating your personalized interview session
- Asking tailored questions based on your role and experience
- Providing real-time feedback on your answers
- Generating a detailed final evaluation

To get started, please provide:
1. Your full name
2. Email address  
3. Position you're applying for
4. Your experience level (entry/mid/senior/lead)

You can also say 'help' at any time for assistance. Let's begin!"""
    )

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🤖 Starting Enhanced AI Interview Agent...")
    print("🔗 Backend API:", BACKEND_URL)
    print("🎤 Using Google Gemini for LLM")
    print("📞 LiveKit integration enabled")
    print("=" * 50)
    
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="AI Interview Agent",
        )
    )
