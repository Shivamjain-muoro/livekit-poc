"""
Simplified Voice Interview Agent
===============================
A practical LiveKit agent for voice-based interviews using available libraries.
This version focuses on core functionality and real-world implementation.
"""

import asyncio
import logging
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Optional, List
from enum import Enum

import aiohttp
import google.generativeai as genai
from dotenv import load_dotenv

# For speech synthesis (using available libraries)
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except ImportError:
    STT_AVAILABLE = False

load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8003")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Google Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterviewState(Enum):
    WAITING = "waiting"
    INTRODUCTION = "introduction"
    QUESTIONING = "questioning"
    LISTENING = "listening"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    ERROR = "error"

class VoiceInterviewAgent:
    """Simplified voice interview agent"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.current_question_id: Optional[str] = None
        self.state = InterviewState.WAITING
        self.candidate_info: Optional[Dict] = None
        self.current_question_index = 0
        self.total_questions = 0
        self.conversation_history: List[Dict] = []
        
        # Initialize TTS
        if TTS_AVAILABLE:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)  # Speaking rate
            self.tts_engine.setProperty('volume', 0.9)  # Volume level
            voices = self.tts_engine.getProperty('voices')
            if voices and len(voices) > 1:
                self.tts_engine.setProperty('voice', voices[1].id)  # Female voice if available
        else:
            self.tts_engine = None
        
        # Initialize STT
        if STT_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
        else:
            self.recognizer = None
            self.microphone = None
            
        # Initialize Gemini for dynamic responses
        if GOOGLE_API_KEY:
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.gemini_model = None
    
    async def start_interview(self):
        """Start the voice interview process"""
        try:
            logger.info(f"Starting voice interview for session: {self.session_id}")
            
            # Get session info
            session_info = await self.get_session_info()
            if not session_info:
                await self.speak("I'm sorry, I couldn't find your interview session.")
                return
            
            self.candidate_info = session_info.get("candidate", {})
            self.total_questions = session_info.get("session", {}).get("total_questions", 5)
            
            # Introduction
            self.state = InterviewState.INTRODUCTION
            welcome_message = f"""
            Hello {self.candidate_info.get('name', 'there')}! 
            Welcome to your voice interview for the {self.candidate_info.get('position', 'position')} role.
            
            I'm your AI interviewer. We'll have {self.total_questions} questions today.
            Please speak clearly after I ask each question.
            
            Let's begin with the first question.
            """
            
            await self.speak(welcome_message)
            await asyncio.sleep(2)  # Brief pause
            
            # Start the first question
            await self.start_first_question()
            
        except Exception as e:
            logger.error(f"Error starting interview: {e}")
            await self.speak("I'm experiencing technical difficulties. Please try again later.")
    
    async def start_first_question(self):
        """Start with the first question"""
        try:
            # Get first question from backend
            response = await self.api_request("POST", f"/api/interview/start/{self.session_id}")
            
            if response and response.get("success"):
                question_data = response.get("first_question", {})
                self.current_question_id = question_data.get("id")
                question_text = question_data.get("question_text")
                
                self.current_question_index = 1
                self.state = InterviewState.QUESTIONING
                
                # Ask the question
                await self.speak(f"Question {self.current_question_index}: {question_text}")
                
                # Listen for answer
                await self.listen_for_answer()
                
            else:
                await self.speak("I couldn't retrieve the first question. Let me try again.")
                
        except Exception as e:
            logger.error(f"Error with first question: {e}")
            await self.speak("I'm having trouble with the questions. Please wait a moment.")
    
    async def listen_for_answer(self):
        """Listen for candidate's answer"""
        if not self.recognizer or not self.microphone:
            logger.warning("Speech recognition not available")
            # Fallback: simulate answer for demo
            await asyncio.sleep(3)
            await self.process_answer("This is a simulated answer for demo purposes.")
            return
        
        try:
            self.state = InterviewState.LISTENING
            await self.speak("Please provide your answer now. I'm listening.")
            
            # Listen for speech with timeout
            with self.microphone as source:
                logger.info("Listening for answer...")
                audio = self.recognizer.listen(source, timeout=30, phrase_time_limit=60)
            
            # Recognize speech
            try:
                answer_text = self.recognizer.recognize_google(audio)
                logger.info(f"Recognized answer: {answer_text}")
                await self.process_answer(answer_text)
            except sr.UnknownValueError:
                await self.speak("I didn't catch that. Could you please repeat your answer?")
                await self.listen_for_answer()
            except sr.RequestError as e:
                logger.error(f"Speech recognition error: {e}")
                await self.speak("I'm having trouble with speech recognition. Let's continue with the next question.")
                await self.move_to_next_question()
                
        except Exception as e:
            logger.error(f"Error listening for answer: {e}")
            await self.speak("I'm having audio issues. Let's continue.")
            await self.move_to_next_question()
    
    async def process_answer(self, answer_text: str):
        """Process the candidate's answer"""
        try:
            self.state = InterviewState.EVALUATING
            
            logger.info(f"Processing answer: {answer_text[:100]}...")
            
            # Submit answer to backend
            response = await self.api_request(
                "POST",
                f"/api/interview/{self.session_id}/answer",
                {
                    "question_id": self.current_question_id,
                    "answer_text": answer_text,
                    "duration": 30  # Estimated duration
                }
            )
            
            if response and response.get("success"):
                feedback = response.get("feedback", {})
                next_question = response.get("next_question")
                is_complete = response.get("is_complete", False)
                
                # Generate dynamic feedback using Gemini
                brief_feedback = await self.generate_dynamic_feedback(answer_text, feedback)
                await self.speak(brief_feedback)
                
                await asyncio.sleep(1)  # Brief pause
                
                if is_complete:
                    await self.complete_interview()
                elif next_question:
                    await self.ask_next_question(next_question)
                else:
                    await self.speak("Let me get the next question for you.")
                    await self.move_to_next_question()
                    
        except Exception as e:
            logger.error(f"Error processing answer: {e}")
            await self.speak("Thank you for your answer. Let's move to the next question.")
            await self.move_to_next_question()
    
    async def generate_dynamic_feedback(self, answer_text: str, feedback: Dict) -> str:
        """Generate dynamic, conversational feedback using Gemini"""
        try:
            if not self.gemini_model:
                return "Thank you for your answer."
            
            prompt = f"""
            You are a friendly AI interviewer. Provide brief, encouraging feedback (1-2 sentences) for this answer:
            
            Answer: {answer_text}
            Score: {feedback.get('score', 3)}/5
            
            Make it conversational and positive, then transition to the next question.
            Don't mention the score directly.
            """
            
            response = await asyncio.to_thread(
                self.gemini_model.generate_content, prompt
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating dynamic feedback: {e}")
            return "Thank you for that thoughtful answer."
    
    async def ask_next_question(self, question_data: Dict):
        """Ask the next question"""
        try:
            self.current_question_id = question_data.get("id")
            question_text = question_data.get("question_text")
            self.current_question_index += 1
            
            self.state = InterviewState.QUESTIONING
            
            await self.speak(f"Question {self.current_question_index}: {question_text}")
            await self.listen_for_answer()
            
        except Exception as e:
            logger.error(f"Error asking next question: {e}")
            await self.complete_interview()
    
    async def move_to_next_question(self):
        """Fallback method to move to next question"""
        try:
            # This could implement logic to get the next question
            # For now, complete the interview
            await self.complete_interview()
        except Exception as e:
            logger.error(f"Error moving to next question: {e}")
            await self.complete_interview()
    
    async def complete_interview(self):
        """Complete the interview"""
        try:
            self.state = InterviewState.COMPLETED
            
            completion_message = f"""
            Thank you for completing the interview! 
            You answered {self.current_question_index} questions.
            
            Your responses have been recorded and will be evaluated.
            We'll be in touch with you soon regarding the next steps.
            
            Have a great day!
            """
            
            await self.speak(completion_message)
            logger.info("Interview completed successfully")
            
        except Exception as e:
            logger.error(f"Error completing interview: {e}")
            await self.speak("Thank you for your time. The interview is now complete.")
    
    async def speak(self, text: str):
        """Convert text to speech"""
        try:
            logger.info(f"Speaking: {text[:100]}...")
            
            if self.tts_engine:
                # Use pyttsx3 for TTS
                await asyncio.to_thread(self._speak_sync, text)
            else:
                # Fallback: just log the text
                logger.info(f"TTS not available. Would say: {text}")
                await asyncio.sleep(2)  # Simulate speaking time
                
        except Exception as e:
            logger.error(f"TTS error: {e}")
    
    def _speak_sync(self, text: str):
        """Synchronous TTS using pyttsx3"""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    async def get_session_info(self) -> Optional[Dict]:
        """Get session information from backend"""
        return await self.api_request("GET", f"/api/interview/session/{self.session_id}")
    
    async def api_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make API request to backend"""
        try:
            url = f"{BACKEND_URL}{endpoint}"
            
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url) as response:
                        if response.status == 200:
                            return await response.json()
                elif method == "POST":
                    async with session.post(url, json=data) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            logger.error(f"API error: {response.status} - {await response.text()}")
                            
        except Exception as e:
            logger.error(f"API request error: {e}")
        
        return None

# Standalone interview runner for testing
async def run_voice_interview(session_id: str):
    """Run a voice interview for testing"""
    agent = VoiceInterviewAgent(session_id)
    await agent.start_interview()

# Demo function
async def demo_interview():
    """Demo function to test the voice interview"""
    print("🎙️ Voice Interview Demo")
    print("This demo simulates a voice interview session.")
    
    # For demo, use a placeholder session ID
    demo_session_id = "demo-session-123"
    
    agent = VoiceInterviewAgent(demo_session_id)
    
    # Simulate interview flow without actual backend
    await agent.speak("Hello! This is a demo of the voice interview system.")
    await asyncio.sleep(2)
    await agent.speak("The system can speak questions and listen to your responses.")
    await asyncio.sleep(2)
    await agent.speak("In a real interview, I would ask technical questions and evaluate your answers.")
    await asyncio.sleep(2)
    await agent.speak("Thank you for trying the demo!")

if __name__ == "__main__":
    print("🚀 Starting Voice Interview Agent Demo")
    
    # Check dependencies
    print(f"TTS Available: {'✅' if TTS_AVAILABLE else '❌ (pip install pyttsx3)'}")
    print(f"STT Available: {'✅' if STT_AVAILABLE else '❌ (pip install SpeechRecognition)'}")
    print(f"Gemini Available: {'✅' if GOOGLE_API_KEY else '❌ (set GOOGLE_API_KEY)'}")
    
    # Run demo
    asyncio.run(demo_interview())
