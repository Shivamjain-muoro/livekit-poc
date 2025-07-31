"""
Voice AI Interview - REAL vs SIMULATION Demonstration
====================================================
This clearly shows the difference between real voice AI and text simulation.
"""

import asyncio
import logging
import json
import os
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice AI vs Simulation Demo", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@dataclass
class InterviewCandidate:
    name: str
    email: str
    position: str

# Global storage
active_sessions: Dict[str, dict] = {}

class InterviewRequest(BaseModel):
    name: str
    email: str
    position: str

@app.post("/start-interview")
async def start_interview(request: InterviewRequest):
    """Start interview session"""
    session_id = str(uuid.uuid4())
    
    active_sessions[session_id] = {
        "candidate": request.dict(),
        "status": "active",
        "start_time": datetime.now()
    }
    
    return {
        "session_id": session_id,
        "status": "ready",
        "message": "Interview session created"
    }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket for real-time communication"""
    await websocket.accept()
    
    if session_id not in active_sessions:
        await websocket.close(code=4004, reason="Session not found")
        return
    
    candidate = active_sessions[session_id]["candidate"]
    
    try:
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "ai_message",
            "text": f"Hello {candidate['name']}! Welcome to your {candidate['position']} interview.",
            "is_simulation": True,  # THIS IS KEY - marking as simulation
            "explanation": "This is TEXT SIMULATION - no real voice is being generated"
        }))
        
        await asyncio.sleep(3)
        
        # Send first question
        await websocket.send_text(json.dumps({
            "type": "ai_question",
            "text": "Could you tell me about yourself and your experience?",
            "is_simulation": True,  # THIS IS KEY - marking as simulation
            "explanation": "This is TEXT SIMULATION - no real voice is being generated"
        }))
        
        # Wait for responses
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "candidate_response":
                    # Send acknowledgment
                    await websocket.send_text(json.dumps({
                        "type": "ai_message",
                        "text": "Thank you for that response. That's very interesting.",
                        "is_simulation": True,  # THIS IS KEY - marking as simulation
                        "explanation": "This is TEXT SIMULATION - no real voice is being generated"
                    }))
                    
                    await asyncio.sleep(2)
                    
                    # Send next question
                    await websocket.send_text(json.dumps({
                        "type": "ai_question", 
                        "text": "Can you describe a challenging project you've worked on?",
                        "is_simulation": True,  # THIS IS KEY - marking as simulation
                        "explanation": "This is TEXT SIMULATION - no real voice is being generated"
                    }))
                    
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if session_id in active_sessions:
            del active_sessions[session_id]

@app.get("/")
async def get_demo_page():
    """Demo page showing the difference between real voice and simulation"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎙️ Real Voice AI vs Text Simulation Demo</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', system-ui, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
                padding: 20px;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto;
            }
            h1 { 
                text-align: center;
                font-size: 2.5rem; 
                margin-bottom: 30px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .comparison {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin: 30px 0;
            }
            .card {
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            .simulation-card {
                border-left: 5px solid #FF6B6B;
            }
            .real-voice-card {
                border-left: 5px solid #4ECDC4;
            }
            .form-group { 
                margin: 15px 0; 
            }
            label { 
                display: block; 
                margin-bottom: 5px; 
                font-weight: 600;
            }
            input, select {
                width: 100%;
                padding: 12px;
                border: none;
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.9);
                color: #333;
                font-size: 16px;
            }
            .btn {
                background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
                color: white;
                padding: 15px 25px;
                border: none;
                border-radius: 25px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                margin: 10px 0;
                width: 100%;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
            }
            .simulation-btn {
                background: linear-gradient(45deg, #FF6B6B, #FF8E8E);
            }
            .real-voice-btn {
                background: linear-gradient(45deg, #4ECDC4, #7FDBDA);
            }
            .status {
                margin: 20px 0;
                padding: 15px;
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-left: 4px solid #4ECDC4;
                min-height: 200px;
                overflow-y: auto;
            }
            .message {
                margin: 10px 0;
                padding: 10px;
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.1);
            }
            .simulation-message {
                background: rgba(255, 107, 107, 0.2);
                border-left: 3px solid #FF6B6B;
            }
            .real-voice-message {
                background: rgba(78, 205, 196, 0.2);
                border-left: 3px solid #4ECDC4;
            }
            .explanation {
                font-size: 12px;
                color: #FFD700;
                margin-top: 5px;
                font-style: italic;
            }
            .warning {
                background: rgba(255, 193, 7, 0.2);
                border: 1px solid #FFC107;
                border-radius: 10px;
                padding: 15px;
                margin: 20px 0;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎙️ Real Voice AI vs Text Simulation</h1>
            
            <div class="warning">
                <h3>⚠️ IMPORTANT: Understanding the Difference</h3>
                <p><strong>Left Side (Red):</strong> Text simulation - NO real voice, just text messages displayed on screen</p>
                <p><strong>Right Side (Blue):</strong> Real voice AI - Actual speech-to-text and text-to-speech using LiveKit</p>
            </div>
            
            <div class="comparison">
                <!-- TEXT SIMULATION SIDE -->
                <div class="card simulation-card">
                    <h2>❌ TEXT SIMULATION</h2>
                    <p>This is what you've been experiencing - no real voice!</p>
                    
                    <div class="form-group">
                        <label for="sim-name">Name:</label>
                        <input type="text" id="sim-name" placeholder="Your name">
                    </div>
                    
                    <div class="form-group">
                        <label for="sim-email">Email:</label>
                        <input type="email" id="sim-email" placeholder="your.email@example.com">
                    </div>
                    
                    <div class="form-group">
                        <label for="sim-position">Position:</label>
                        <select id="sim-position">
                            <option value="">Select position</option>
                            <option value="Software Developer">Software Developer</option>
                            <option value="Data Scientist">Data Scientist</option>
                            <option value="Product Manager">Product Manager</option>
                        </select>
                    </div>
                    
                    <button class="btn simulation-btn" onclick="startSimulation()">
                        📝 Start Text Simulation (No Voice)
                    </button>
                    
                    <div class="status" id="simulationStatus">
                        <p>This will show text messages pretending to be AI speech, but no actual voice will be heard.</p>
                    </div>
                </div>
                
                <!-- REAL VOICE AI SIDE -->
                <div class="card real-voice-card">
                    <h2>✅ REAL VOICE AI</h2>
                    <p>This would use actual LiveKit voice capabilities!</p>
                    
                    <div class="form-group">
                        <label for="voice-name">Name:</label>
                        <input type="text" id="voice-name" placeholder="Your name">
                    </div>
                    
                    <div class="form-group">
                        <label for="voice-email">Email:</label>
                        <input type="email" id="voice-email" placeholder="your.email@example.com">
                    </div>
                    
                    <div class="form-group">
                        <label for="voice-position">Position:</label>
                        <select id="voice-position">
                            <option value="">Select position</option>
                            <option value="Software Developer">Software Developer</option>
                            <option value="Data Scientist">Data Scientist</option>
                            <option value="Product Manager">Product Manager</option>
                        </select>
                    </div>
                    
                    <button class="btn real-voice-btn" onclick="startRealVoice()">
                        🎤 Start Real Voice AI (Requires LiveKit Server)
                    </button>
                    
                    <div class="status" id="voiceStatus">
                        <p><strong>Status:</strong> LiveKit server required for real voice AI</p>
                        <p><strong>Requirements:</strong></p>
                        <ul>
                            <li>LiveKit server running on port 7880</li>
                            <li>LiveKit Agents with STT/TTS</li>
                            <li>Real-time audio processing</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let simulationWs = null;
            let simulationSessionId = null;
            
            async function startSimulation() {
                const name = document.getElementById('sim-name').value.trim();
                const email = document.getElementById('sim-email').value.trim();
                const position = document.getElementById('sim-position').value;
                
                if (!name || !email || !position) {
                    alert('Please fill in all fields');
                    return;
                }
                
                try {
                    // Create session
                    const response = await fetch('/start-interview', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name, email, position })
                    });
                    
                    const data = await response.json();
                    simulationSessionId = data.session_id;
                    
                    // Connect WebSocket
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    simulationWs = new WebSocket(`${protocol}//${window.location.host}/ws/${simulationSessionId}`);
                    
                    const statusDiv = document.getElementById('simulationStatus');
                    statusDiv.innerHTML = '<p><strong>TEXT SIMULATION ACTIVE:</strong></p>';
                    
                    simulationWs.onmessage = (event) => {
                        const message = JSON.parse(event.data);
                        
                        const messageDiv = document.createElement('div');
                        messageDiv.className = 'message simulation-message';
                        messageDiv.innerHTML = `
                            <strong>AI:</strong> ${message.text}
                            <div class="explanation">${message.explanation}</div>
                        `;
                        statusDiv.appendChild(messageDiv);
                        statusDiv.scrollTop = statusDiv.scrollHeight;
                        
                        // Auto-respond after 3 seconds
                        if (message.type === 'ai_question') {
                            setTimeout(() => {
                                simulationWs.send(JSON.stringify({
                                    type: 'candidate_response',
                                    text: 'This is a simulated response from the candidate.'
                                }));
                                
                                const responseDiv = document.createElement('div');
                                responseDiv.className = 'message';
                                responseDiv.innerHTML = `
                                    <strong>You:</strong> This is a simulated response from the candidate.
                                    <div class="explanation">This simulates typing a response</div>
                                `;
                                statusDiv.appendChild(responseDiv);
                                statusDiv.scrollTop = statusDiv.scrollHeight;
                            }, 3000);
                        }
                    };
                    
                } catch (error) {
                    console.error('Error:', error);
                    alert('Failed to start simulation');
                }
            }
            
            function startRealVoice() {
                const statusDiv = document.getElementById('voiceStatus');
                statusDiv.innerHTML = `
                    <p><strong>❌ REAL VOICE AI NOT AVAILABLE</strong></p>
                    <p>To enable real voice AI, you need:</p>
                    <ol>
                        <li>Start LiveKit server: <code>livekit-server --dev --port 7880</code></li>
                        <li>Install LiveKit Agents: <code>pip install livekit-agents[codecs,openai]</code></li>
                        <li>Configure STT/TTS providers (OpenAI, Google Cloud, etc.)</li>
                        <li>Run the voice agent script</li>
                    </ol>
                    <p><strong>The current system only shows text simulation - NO real voice is being generated!</strong></p>
                `;
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    print("🎙️ Voice AI vs Simulation Demo")
    print("=" * 50)
    print("🔴 IMPORTANT: This clearly demonstrates the difference between:")
    print("   📝 Text Simulation (what you've been experiencing)")
    print("   🎤 Real Voice AI (what would be actual voice)")
    print("")
    print("🌐 Open: http://localhost:8001")
    print("   Left side = Text simulation (no real voice)")
    print("   Right side = Real voice AI requirements")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
