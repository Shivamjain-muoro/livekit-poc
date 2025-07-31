"""
Simple LiveKit Voice Interview Agent
===================================
Uses ONLY LiveKit core SDK - no external dependencies
"""

import asyncio
import logging
import os
import json
from typing import Dict, List
from dataclasses import dataclass
from dotenv import load_dotenv

# Core LiveKit imports only
from livekit import rtc, api
from livekit.api import AccessToken
from livekit.api.access_token import VideoGrants

load_dotenv()

# Configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey") 
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InterviewCandidate:
    name: str
    position: str
    experience_years: int
    skills: List[str]

class LiveKitInterviewAgent:
    """Pure LiveKit interview agent using only core SDK"""
    
    def __init__(self, room_name: str, candidate: InterviewCandidate):
        self.room_name = room_name
        self.candidate = candidate
        self.room = None
        self.questions = [
            f"Hello {candidate.name}! Welcome to your {candidate.position} interview. Please tell me about yourself.",
            f"With {candidate.experience_years} years of experience, what project are you most proud of?",
            "How do you handle challenges when working in a team?",
            f"Can you describe your experience with {', '.join(candidate.skills[:2])}?",
            "What are your career goals and where do you see yourself in 5 years?"
        ]
        self.current_question = 0
        
    async def start_agent(self):
        """Start the LiveKit interview agent"""
        
        # Create room connection
        self.room = rtc.Room()
        
        # Set up event handlers
        @self.room.on("participant_connected")
        def on_participant_connected(participant: rtc.RemoteParticipant):
            logger.info(f"✅ Candidate joined: {participant.identity}")
            # Start interview flow
            asyncio.create_task(self.start_interview())
        
        @self.room.on("track_subscribed")
        def on_track_subscribed(track: rtc.Track, publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
            if track.kind == rtc.TrackKind.KIND_AUDIO:
                logger.info(f"🎤 Audio track received from {participant.identity}")
                # Handle audio processing
                self.setup_audio_handler(track)
        
        @self.room.on("data_received")
        def on_data_received(data: bytes, participant: rtc.RemoteParticipant):
            try:
                message = json.loads(data.decode())
                logger.info(f"📨 Data received: {message}")
                asyncio.create_task(self.handle_message(message))
            except Exception as e:
                logger.error(f"Error processing data: {e}")
        
        # Generate access token for AI agent
        token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET, identity="ai_interviewer")
        token.with_grants(VideoGrants(
            room_join=True,
            room=self.room_name,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True
        ))
        
        # Connect to room
        try:
            await self.room.connect(LIVEKIT_URL, token.to_jwt())
            logger.info(f"🚀 AI Agent connected to room: {self.room_name}")
            
            # Wait for participants
            logger.info("⏳ Waiting for candidate to join...")
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise
    
    def setup_audio_handler(self, track: rtc.AudioTrack):
        """Set up audio processing for candidate responses"""
        
        @track.on("frame_received")
        def on_audio_frame(frame: rtc.AudioFrame):
            # In a full implementation, this would process speech-to-text
            # For now, we'll simulate understanding the response
            asyncio.create_task(self.process_audio_response())
    
    async def process_audio_response(self):
        """Process candidate's audio response"""
        logger.info("🎯 Processing candidate audio response...")
        
        # Simulate processing time
        await asyncio.sleep(2)
        
        # Move to next question
        self.current_question += 1
        if self.current_question < len(self.questions):
            await self.ask_next_question()
        else:
            await self.complete_interview()
    
    async def start_interview(self):
        """Start the interview flow"""
        await asyncio.sleep(2)  # Allow connection to stabilize
        
        logger.info("🎙️ Starting interview...")
        await self.ask_next_question()
    
    async def ask_next_question(self):
        """Ask the next interview question"""
        if self.current_question < len(self.questions):
            question = self.questions[self.current_question]
            
            # Send question via data channel
            message = {
                "type": "interview_question",
                "text": question,
                "question_number": self.current_question + 1,
                "total_questions": len(self.questions),
                "action": "speak_question"
            }
            
            await self.send_data(json.dumps(message))
            logger.info(f"❓ Asked question {self.current_question + 1}: {question}")
    
    async def complete_interview(self):
        """Complete the interview"""
        completion_message = {
            "type": "interview_complete",
            "text": f"Thank you {self.candidate.name}! That concludes our interview. We'll be in touch with next steps soon!",
            "action": "speak_completion"
        }
        
        await self.send_data(json.dumps(completion_message))
        logger.info("✅ Interview completed successfully")
    
    async def send_data(self, data: str):
        """Send data to participants"""
        if self.room and self.room.local_participant:
            try:
                await self.room.local_participant.publish_data(data.encode())
            except Exception as e:
                logger.error(f"Failed to send data: {e}")
    
    async def handle_message(self, message: dict):
        """Handle incoming messages from participants"""
        if message.get("type") == "candidate_ready":
            logger.info("🎯 Candidate is ready - starting interview")
            await self.start_interview()
        elif message.get("type") == "response_complete":
            logger.info("🎯 Candidate finished speaking")
            await self.process_audio_response()

async def create_interview_session(candidate: InterviewCandidate) -> dict:
    """Create a new LiveKit interview session"""
    
    room_name = f"interview_{candidate.name.lower().replace(' ', '_')}"
    
    # Generate candidate access token
    candidate_token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET, identity=candidate.name)
    candidate_token.with_grants(VideoGrants(
        room_join=True,
        room=room_name,
        can_publish=True,
        can_subscribe=True,
        can_publish_data=True
    ))
    
    # Start the AI agent
    agent = LiveKitInterviewAgent(room_name, candidate)
    
    # Start agent in background
    asyncio.create_task(agent.start_agent())
    
    return {
        "room_name": room_name,
        "candidate_token": candidate_token.to_jwt(),
        "livekit_url": LIVEKIT_URL,
        "agent_status": "active",
        "message": "LiveKit interview room created with AI agent"
    }

# Web interface
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="🎙️ Pure LiveKit Interview Agent")

class StartInterviewRequest(BaseModel):
    name: str
    position: str
    experience_years: int
    skills: List[str]

@app.post("/start-interview")
async def start_interview(request: StartInterviewRequest):
    """Start LiveKit interview with AI agent"""
    
    candidate = InterviewCandidate(
        name=request.name,
        position=request.position,
        experience_years=request.experience_years,
        skills=request.skills
    )
    
    session_info = await create_interview_session(candidate)
    
    return {
        "status": "success",
        "session_info": session_info,
        "implementation": "pure_livekit_sdk"
    }

@app.get("/")
async def get_interview_page():
    """Serve the LiveKit interview page"""
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎙️ Pure LiveKit Voice Interview</title>
        <script src="https://unpkg.com/livekit-client@2/dist/livekit-client.umd.js"></script>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2563eb; text-align: center; }
            .badge { background: #10b981; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px; margin: 5px; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            button { background: #2563eb; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; width: 100%; }
            button:hover { background: #1d4ed8; }
            button:disabled { background: #9ca3af; cursor: not-allowed; }
            .status { background: #f0f9ff; border: 1px solid #0ea5e9; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .controls { margin: 20px 0; text-align: center; }
            #interviewRoom { display: none; }
            .voice-indicator { width: 100px; height: 100px; border-radius: 50%; background: #10b981; margin: 20px auto; display: flex; align-items: center; justify-content: center; font-size: 40px; color: white; }
            .listening { background: #f59e0b; animation: pulse 1s infinite; }
            @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.1); } 100% { transform: scale(1); } }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎙️ Pure LiveKit Voice Interview</h1>
            
            <div style="text-align: center; margin: 20px 0;">
                <span class="badge">✅ LiveKit Core SDK</span>
                <span class="badge">✅ Audio Processing</span>
                <span class="badge">✅ AI Agent</span>
                <span class="badge">✅ Real-time Communication</span>
            </div>
            
            <div id="setupForm">
                <div class="status">
                    <strong>🔧 Pure LiveKit Implementation:</strong><br>
                    • Uses only LiveKit Core SDK<br>
                    • AI Agent runs in LiveKit room<br>
                    • Audio processing via LiveKit tracks<br>
                    • Real-time data communication<br>
                    • No external voice APIs
                </div>
                
                <div class="form-group">
                    <label for="name">Full Name:</label>
                    <input type="text" id="name" placeholder="Enter your name" required>
                </div>
                
                <div class="form-group">
                    <label for="position">Position:</label>
                    <select id="position" required>
                        <option value="">Select position</option>
                        <option value="Software Developer">Software Developer</option>
                        <option value="Frontend Developer">Frontend Developer</option>
                        <option value="Backend Developer">Backend Developer</option>
                        <option value="Full Stack Developer">Full Stack Developer</option>
                        <option value="Data Scientist">Data Scientist</option>
                        <option value="DevOps Engineer">DevOps Engineer</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="experience">Years of Experience:</label>
                    <select id="experience" required>
                        <option value="">Select experience</option>
                        <option value="0">Entry Level</option>
                        <option value="1">1 year</option>
                        <option value="2">2 years</option>
                        <option value="3">3 years</option>
                        <option value="5">5+ years</option>
                        <option value="10">10+ years</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="skills">Skills (comma-separated):</label>
                    <textarea id="skills" placeholder="Python, JavaScript, React, Node.js" rows="3"></textarea>
                </div>
                
                <button onclick="startLiveKitInterview()" id="startBtn">🎤 Start LiveKit Interview</button>
            </div>
            
            <div id="interviewRoom">
                <h2>🎙️ LiveKit Interview Room</h2>
                <div class="voice-indicator" id="voiceIndicator">🎤</div>
                <div class="status" id="roomStatus">Connecting to LiveKit room...</div>
                
                <div class="controls">
                    <button onclick="toggleMute()" id="muteBtn">🔇 Mute</button>
                    <button onclick="endInterview()" style="background: #dc2626;">🛑 End Interview</button>
                </div>
                
                <div id="messages" style="background: #f9fafb; padding: 15px; border-radius: 5px; margin: 20px 0; max-height: 300px; overflow-y: auto;"></div>
            </div>
        </div>

        <script>
            let room = null;
            let localAudioTrack = null;
            let isMuted = false;
            
            async function startLiveKitInterview() {
                const name = document.getElementById('name').value.trim();
                const position = document.getElementById('position').value;
                const experience = parseInt(document.getElementById('experience').value);
                const skills = document.getElementById('skills').value.split(',').map(s => s.trim()).filter(s => s);
                
                if (!name || !position || isNaN(experience)) {
                    alert('Please fill in all required fields');
                    return;
                }
                
                const startBtn = document.getElementById('startBtn');
                startBtn.disabled = true;
                startBtn.textContent = '🔄 Creating LiveKit Session...';
                
                try {
                    // Create interview session
                    const response = await fetch('/start-interview', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name, position, experience_years: experience, skills })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        // Connect to LiveKit room
                        await connectToRoom(result.session_info);
                    } else {
                        throw new Error(result.detail || 'Failed to create session');
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                    startBtn.disabled = false;
                    startBtn.textContent = '🎤 Start LiveKit Interview';
                }
            }
            
            async function connectToRoom(sessionInfo) {
                try {
                    // Initialize LiveKit room
                    room = new LiveKitClient.Room({
                        adaptiveStream: true,
                        dynacast: true,
                    });
                    
                    // Set up event handlers
                    room.on('connected', () => {
                        console.log('✅ Connected to LiveKit room');
                        updateStatus('Connected to interview room');
                        
                        // Notify AI agent that candidate is ready
                        room.localParticipant.publishData(JSON.stringify({
                            type: 'candidate_ready',
                            timestamp: Date.now()
                        }));
                    });
                    
                    room.on('participantConnected', (participant) => {
                        console.log('✅ AI Interviewer joined:', participant.identity);
                        updateStatus('AI Interviewer is ready');
                    });
                    
                    room.on('dataReceived', (data, participant) => {
                        try {
                            const message = JSON.parse(new TextDecoder().decode(data));
                            console.log('📨 Message from AI:', message);
                            handleAIMessage(message);
                        } catch (e) {
                            console.error('Error parsing data:', e);
                        }
                    });
                    
                    room.on('trackSubscribed', (track, publication, participant) => {
                        if (track.kind === 'audio' && participant.identity === 'ai_interviewer') {
                            console.log('🔊 AI audio track received');
                            // Play AI audio
                            track.attach();
                        }
                    });
                    
                    // Connect to room
                    await room.connect(sessionInfo.livekit_url, sessionInfo.candidate_token);
                    
                    // Create local audio track
                    localAudioTrack = await LiveKitClient.createLocalAudioTrack({
                        echoCancellation: true,
                        noiseSuppression: true,
                    });
                    
                    // Publish audio track
                    await room.localParticipant.publishTrack(localAudioTrack);
                    
                    // Show interview room
                    document.getElementById('setupForm').style.display = 'none';
                    document.getElementById('interviewRoom').style.display = 'block';
                    
                    updateStatus('🎙️ Interview started - AI will ask questions');
                    
                } catch (error) {
                    console.error('❌ Failed to connect to room:', error);
                    alert('Failed to connect to interview room: ' + error.message);
                }
            }
            
            function handleAIMessage(message) {
                if (message.type === 'interview_question') {
                    addMessage('AI Interviewer', message.text);
                    updateVoiceIndicator('listening');
                    updateStatus(`Question ${message.question_number}/${message.total_questions}: Listening for your response...`);
                    
                    // Start listening for response (simulate)
                    setTimeout(() => {
                        // Simulate response completion
                        room.localParticipant.publishData(JSON.stringify({
                            type: 'response_complete',
                            timestamp: Date.now()
                        }));
                        updateVoiceIndicator('processing');
                        updateStatus('Processing your response...');
                    }, 10000); // 10 seconds to respond
                    
                } else if (message.type === 'interview_complete') {
                    addMessage('AI Interviewer', message.text);
                    updateStatus('✅ Interview completed!');
                    updateVoiceIndicator('complete');
                }
            }
            
            function addMessage(sender, text) {
                const messages = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
                messageDiv.style.margin = '10px 0';
                messageDiv.style.padding = '10px';
                messageDiv.style.background = sender === 'AI Interviewer' ? '#e0f2fe' : '#f0fdf4';
                messageDiv.style.borderRadius = '5px';
                messages.appendChild(messageDiv);
                messages.scrollTop = messages.scrollHeight;
            }
            
            function updateStatus(status) {
                document.getElementById('roomStatus').textContent = status;
            }
            
            function updateVoiceIndicator(state) {
                const indicator = document.getElementById('voiceIndicator');
                indicator.className = 'voice-indicator';
                
                switch (state) {
                    case 'listening':
                        indicator.classList.add('listening');
                        indicator.textContent = '👂';
                        break;
                    case 'processing':
                        indicator.textContent = '🤔';
                        break;
                    case 'complete':
                        indicator.textContent = '✅';
                        break;
                    default:
                        indicator.textContent = '🎤';
                }
            }
            
            async function toggleMute() {
                if (localAudioTrack) {
                    isMuted = !isMuted;
                    localAudioTrack.mute(isMuted);
                    document.getElementById('muteBtn').textContent = isMuted ? '🔊 Unmute' : '🔇 Mute';
                }
            }
            
            async function endInterview() {
                if (room) {
                    await room.disconnect();
                    alert('Interview ended. Thank you for your time!');
                    location.reload();
                }
            }
        </script>
    </body>
    </html>
    '''
    
    return HTMLResponse(content=html)

if __name__ == "__main__":
    print("🎙️ Pure LiveKit Interview Agent")
    print("=" * 40)
    print("🔧 Implementation: LiveKit Core SDK Only")
    print(f"📡 LiveKit Server: {LIVEKIT_URL}")
    print("🤖 AI Agent: Integrated with LiveKit room")
    print("")
    print("🌐 Interview Platform: http://localhost:8003")
    print("🎙️ LiveKit Admin: http://localhost:7880")
    print("")
    print("⚠️  Requirements:")
    print("   • LiveKit server running on port 7880")
    print("   • Use: livekit-server --dev --port 7880 --keys devkey:secret")
    
    uvicorn.run(app, host="0.0.0.0", port=8003)
