"""
LIVEKIT LOCAL SYSTEM ARCHITECTURE EXPLANATION
Complete flow from HTML frontend to AI agent backend
"""

print("""
🏗️ LIVEKIT SYSTEM ARCHITECTURE - COMPLETE FLOW
================================================================

WHY HTML FILES ARE NEEDED:
LiveKit is a WebRTC-based real-time communication platform that requires:
1. A WEB CLIENT (HTML/JavaScript) for the candidate
2. A SERVER AGENT (Python) for the AI interviewer

Think of it like Zoom or Google Meet:
- You need a web browser interface to join meetings
- The AI agent acts like another participant in the meeting

================================================================

🔄 COMPLETE WORKFLOW:

1. CANDIDATE SIDE (Web Browser - HTML):
   ┌─────────────────────────────────────────────────────────┐
   │  📱 Candidate opens: http://localhost:8080/interview.html │
   │  🎤 Browser requests microphone access                   │
   │  🌐 JavaScript connects to LiveKit server                │
   │  📡 Establishes WebRTC connection                        │
   │  🎙️ Sends audio stream to LiveKit server                │
   └─────────────────────────────────────────────────────────┘
                                   │
                                   ▼
2. LIVEKIT SERVER (Docker Container):
   ┌─────────────────────────────────────────────────────────┐
   │  🐳 Running on: ws://localhost:7880                     │
   │  📊 Manages WebRTC connections                          │
   │  🔄 Routes audio between participants                   │
   │  📋 Creates virtual "rooms" for interviews              │
   │  🔐 Handles authentication with JWT tokens              │
   └─────────────────────────────────────────────────────────┘
                                   │
                                   ▼
3. AI AGENT SIDE (Python Backend):
   ┌─────────────────────────────────────────────────────────┐
   │  🤖 Python script: complete_interview_agent.py         │
   │  🎧 Connects to LiveKit as another "participant"       │
   │  🧠 Uses Google Gemini for real-time voice processing  │
   │  📝 Automatically records Q&A exchanges                │
   │  💾 Saves evaluations to SQLite database               │
   └─────────────────────────────────────────────────────────┘

================================================================

🌐 HTML FILES BREAKDOWN:

📄 web/index.html - INTERVIEW PORTAL:
Purpose: Landing page for creating interview sessions
Features:
- Generate unique interview rooms
- Create JWT tokens for access
- System status monitoring
- Professional candidate interface

📄 web/interview.html - MEETING ROOM:
Purpose: Actual interview interface (like Zoom meeting room)
Features:
- WebRTC audio/video connection
- Real-time conversation with AI
- Microphone/camera controls
- Interview transcript display
- Connection status monitoring

================================================================

🔧 CONFIGURATION FLOW:

1. Environment (.env):
   LIVEKIT_URL=ws://localhost:7880  ← Where to connect
   LIVEKIT_API_KEY=devkey           ← Authentication key
   LIVEKIT_API_SECRET=secret        ← Secret for JWT tokens

2. LiveKit Server (livekit.yaml):
   port: 7880                       ← Server listening port
   keys: devkey: secret             ← API authentication
   development: true                ← Local dev mode

3. HTML Frontend:
   - Connects to ws://localhost:7880
   - Uses JWT tokens for room access
   - Establishes WebRTC for real-time audio

4. Python Agent:
   - Connects to same LiveKit server
   - Joins the same room as candidate
   - Processes audio with Google Gemini

================================================================

🎯 WHY THIS ARCHITECTURE:

✅ SEPARATION OF CONCERNS:
- HTML handles user interface and WebRTC
- LiveKit handles real-time communication
- Python handles AI processing and evaluation

✅ SCALABILITY:
- Multiple candidates can interview simultaneously
- Each gets their own "room"
- AI agent can handle multiple rooms

✅ REAL-TIME PERFORMANCE:
- WebRTC provides low-latency audio
- Direct browser-to-server connection
- No audio quality loss

✅ BROWSER COMPATIBILITY:
- Works in any modern web browser
- No software installation required
- Cross-platform (Windows, Mac, Linux)

================================================================

🔄 STEP-BY-STEP INTERVIEW FLOW:

1. Candidate clicks interview link
2. Browser opens web/interview.html
3. JavaScript requests microphone access
4. LiveKit client connects to ws://localhost:7880
5. AI agent detects new participant in room
6. Agent starts interview conversation
7. Candidate speaks → Browser captures audio → LiveKit routes to agent
8. Agent processes with Google Gemini → Responds with audio
9. Agent automatically records Q&A and evaluates
10. Interview ends → Agent saves complete evaluation

================================================================

🚀 ALTERNATIVES (Why we chose this approach):

❌ Direct Python Audio Capture:
- Would require candidate to install Python
- Complex audio device management
- No web browser compatibility

❌ Simple REST API:
- No real-time voice conversation
- Would be text-based only
- Not a natural interview experience

✅ LiveKit + HTML (Our Choice):
- Professional video conference experience
- Real-time voice conversation
- Browser-based (no installation)
- Scalable and maintainable

================================================================

This is exactly how companies like Zoom, Google Meet, and Microsoft Teams work:
- Web frontend for user interface
- Media server for real-time communication
- Backend services for processing and storage

""")

if __name__ == "__main__":
    pass
