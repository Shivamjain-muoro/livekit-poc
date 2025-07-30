"""
Simplified LiveKit Client with Mock Implementation
================================================
This client provides a working interface for testing the interview flow
without requiring the full LiveKit JavaScript library.
"""

from flask import Flask, render_template_string, request, jsonify
import requests
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Backend configuration
BACKEND_URL = "http://localhost:8002"
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://testpoc-mys8x433.livekit.cloud")

# HTML template with mock LiveKit implementation
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LiveKit AI Interview - Simplified</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .main-content {
            padding: 40px;
        }

        .form-section {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }

        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }

        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.3s;
            margin: 10px;
        }

        .btn:hover {
            transform: translateY(-2px);
        }

        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }

        .video-section {
            display: none;
            background: #000;
            border-radius: 15px;
            padding: 20px;
            margin-top: 30px;
        }

        .video-container {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }

        .video-element {
            flex: 1;
            min-width: 300px;
            border-radius: 10px;
            overflow: hidden;
        }

        .video-element video {
            width: 100%;
            height: 300px;
            object-fit: cover;
            background: #333;
        }

        .video-placeholder {
            width: 100%;
            height: 300px;
            background: linear-gradient(45deg, #333, #555);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 18px;
            border-radius: 10px;
        }

        .video-label {
            color: white;
            font-weight: 600;
            margin-bottom: 10px;
            text-align: center;
        }

        .controls {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 20px;
        }

        .status {
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            font-weight: 600;
        }

        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .status.info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }

        .chat-container {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            max-height: 400px;
            overflow-y: auto;
        }

        .chat-message {
            margin: 10px 0;
            padding: 10px 15px;
            border-radius: 10px;
        }

        .chat-message.ai {
            background: #e3f2fd;
            margin-left: 20px;
        }

        .chat-message.user {
            background: #f3e5f5;
            margin-right: 20px;
        }

        .hidden {
            display: none;
        }

        .interview-simulator {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }

        .interview-simulator h3 {
            color: #856404;
            margin-bottom: 15px;
        }

        .speaking-indicator {
            display: inline-block;
            padding: 5px 10px;
            background: #28a745;
            color: white;
            border-radius: 15px;
            font-size: 12px;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎤 LiveKit AI Interview</h1>
            <p>Real-time Voice & Video Interview with AI Agent</p>
        </div>

        <div class="main-content">
            <!-- Interview Setup Form -->
            <div id="setupForm" class="form-section">
                <h2>Start Your Interview</h2>
                
                <div class="form-group">
                    <label for="name">Your Name:</label>
                    <input type="text" id="name" placeholder="Enter your full name" required>
                </div>

                <div class="form-group">
                    <label for="position">Position Applied For:</label>
                    <select id="position" required>
                        <option value="">Select a position</option>
                        <option value="Frontend Developer">Frontend Developer</option>
                        <option value="Backend Developer">Backend Developer</option>
                        <option value="Full Stack Developer">Full Stack Developer</option>
                        <option value="DevOps Engineer">DevOps Engineer</option>
                        <option value="Data Scientist">Data Scientist</option>
                        <option value="Mobile Developer">Mobile Developer</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="experience">Years of Experience:</label>
                    <select id="experience" required>
                        <option value="">Select experience level</option>
                        <option value="0-1">0-1 years (Entry Level)</option>
                        <option value="2-3">2-3 years (Junior)</option>
                        <option value="4-6">4-6 years (Mid Level)</option>
                        <option value="7-10">7-10 years (Senior)</option>
                        <option value="10+">10+ years (Expert)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="skills">Technical Skills (comma-separated):</label>
                    <textarea id="skills" rows="3" placeholder="e.g., JavaScript, Python, React, Node.js, AWS"></textarea>
                </div>

                <button class="btn" onclick="startInterview()">Start Live Interview</button>
            </div>

            <!-- Status Messages -->
            <div id="statusContainer"></div>

            <!-- Video Section -->
            <div id="videoSection" class="video-section">
                <h3 style="color: white; text-align: center; margin-bottom: 20px;">Live Interview Session <span id="speakingIndicator" class="speaking-indicator hidden">🎤 AI Speaking</span></h3>
                
                <div class="video-container">
                    <div class="video-element">
                        <div class="video-label">Your Video</div>
                        <div class="video-placeholder" id="localVideoPlaceholder">
                            📹 Your Camera Feed<br>
                            <small>(Camera access required)</small>
                        </div>
                        <video id="localVideo" autoplay muted style="display: none;"></video>
                    </div>
                    <div class="video-element">
                        <div class="video-label">AI Interviewer</div>
                        <div class="video-placeholder">
                            🤖 AI Interviewer<br>
                            <small>(Audio-only conversation)</small>
                        </div>
                    </div>
                </div>

                <div class="controls">
                    <button class="btn" id="muteBtn" onclick="toggleMute()">🎤 Mute</button>
                    <button class="btn" id="videoBtn" onclick="toggleVideo()">📹 Video Off</button>
                    <button class="btn" onclick="endInterview()" style="background: #dc3545;">End Interview</button>
                </div>
            </div>

            <!-- Interview Simulator -->
            <div id="interviewSimulator" class="interview-simulator hidden">
                <h3>🎙️ Interview in Progress</h3>
                <p>This is a simulated LiveKit session. In a real implementation, you would be connected to the AI agent via WebRTC.</p>
                <button class="btn" onclick="simulateAIQuestion()">Simulate AI Question</button>
            </div>

            <!-- Chat Container -->
            <div id="chatContainer" class="chat-container hidden">
                <h4>Interview Conversation</h4>
                <div id="chatMessages"></div>
            </div>
        </div>
    </div>

    <script>
        let sessionData = null;
        let isAudioMuted = false;
        let isVideoOff = false;
        let interviewQuestions = [
            "Tell me about yourself and your programming background.",
            "What programming languages are you most comfortable with?",
            "Describe a challenging project you've worked on recently.",
            "How do you approach debugging complex issues?",
            "What's your experience with version control systems like Git?",
            "Tell me about a time you had to learn a new technology quickly.",
            "How do you ensure code quality in your projects?",
            "What interests you most about this position?"
        ];
        let currentQuestionIndex = 0;

        // Show status messages
        function showStatus(message, type = 'info') {
            const container = document.getElementById('statusContainer');
            const statusDiv = document.createElement('div');
            statusDiv.className = `status ${type}`;
            statusDiv.textContent = message;
            container.innerHTML = '';
            container.appendChild(statusDiv);
            
            // Auto-remove after 5 seconds for non-error messages
            if (type !== 'error') {
                setTimeout(() => {
                    statusDiv.remove();
                }, 5000);
            }
        }

        // Add chat message
        function addChatMessage(sender, message) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${sender}`;
            messageDiv.innerHTML = `<strong>${sender === 'ai' ? 'AI Interviewer' : 'You'}:</strong> ${message}`;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Show chat container if hidden
            document.getElementById('chatContainer').classList.remove('hidden');
        }

        // Start interview process
        async function startInterview() {
            const name = document.getElementById('name').value.trim();
            const position = document.getElementById('position').value;
            const experience = document.getElementById('experience').value;
            const skills = document.getElementById('skills').value.trim();

            if (!name || !position || !experience) {
                showStatus('Please fill in all required fields', 'error');
                return;
            }

            try {
                showStatus('Creating interview session...', 'info');

                // Create session with backend
                const response = await fetch('{{ backend_url }}/api/sessions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        candidate: {
                            name: name,
                            email: name.toLowerCase().replace(/\\s+/g, '.') + '@example.com',
                            position: position,
                            experience_level: experience
                        },
                        interview_type: "technical"
                    })
                });

                if (!response.ok) {
                    throw new Error(`Failed to create session: ${response.status}`);
                }

                sessionData = await response.json();
                console.log('Session created:', sessionData);

                showStatus('Session created! Starting interview...', 'success');

                // Simulate LiveKit connection
                setTimeout(() => {
                    startSimulatedInterview();
                }, 1000);

            } catch (error) {
                console.error('Error starting interview:', error);
                showStatus(`Error: ${error.message}`, 'error');
            }
        }

        // Start simulated interview
        async function startSimulatedInterview() {
            showStatus('Connected to interview room!', 'success');
            document.getElementById('setupForm').style.display = 'none';
            document.getElementById('videoSection').style.display = 'block';
            document.getElementById('interviewSimulator').classList.remove('hidden');

            // Try to access camera
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
                const localVideo = document.getElementById('localVideo');
                localVideo.srcObject = stream;
                localVideo.style.display = 'block';
                document.getElementById('localVideoPlaceholder').style.display = 'none';
                addChatMessage('user', 'Camera and microphone connected successfully!');
            } catch (error) {
                console.log('Camera access denied or not available:', error);
                addChatMessage('user', 'Camera access not available, but interview can continue with text.');
            }

            // Start the interview
            setTimeout(() => {
                addChatMessage('ai', 'Welcome! I\'m your AI interviewer. Let\'s begin with some questions.');
                setTimeout(() => {
                    askNextQuestion();
                }, 2000);
            }, 1000);
        }

        // Ask next question
        function askNextQuestion() {
            if (currentQuestionIndex < interviewQuestions.length) {
                const question = interviewQuestions[currentQuestionIndex];
                addChatMessage('ai', question);
                
                // Show speaking indicator
                const indicator = document.getElementById('speakingIndicator');
                indicator.classList.remove('hidden');
                setTimeout(() => {
                    indicator.classList.add('hidden');
                }, 3000);
                
                currentQuestionIndex++;
            } else {
                addChatMessage('ai', 'Thank you for the interview! We\'ll be in touch soon.');
                setTimeout(() => {
                    endInterview();
                }, 3000);
            }
        }

        // Simulate AI question (manual trigger)
        function simulateAIQuestion() {
            askNextQuestion();
        }

        // Toggle microphone
        function toggleMute() {
            isAudioMuted = !isAudioMuted;
            const muteBtn = document.getElementById('muteBtn');
            muteBtn.textContent = isAudioMuted ? '🔇 Unmute' : '🎤 Mute';
            addChatMessage('user', `Microphone ${isAudioMuted ? 'muted' : 'unmuted'}`);
        }

        // Toggle video
        function toggleVideo() {
            isVideoOff = !isVideoOff;
            const videoBtn = document.getElementById('videoBtn');
            const localVideo = document.getElementById('localVideo');
            
            videoBtn.textContent = isVideoOff ? '📹 Video On' : '📹 Video Off';
            
            if (localVideo.srcObject) {
                const videoTrack = localVideo.srcObject.getVideoTracks()[0];
                if (videoTrack) {
                    videoTrack.enabled = !isVideoOff;
                }
            }
            
            addChatMessage('user', `Camera ${isVideoOff ? 'turned off' : 'turned on'}`);
        }

        // End interview
        function endInterview() {
            showStatus('Interview ended. Thank you!', 'info');
            document.getElementById('videoSection').style.display = 'none';
            document.getElementById('interviewSimulator').classList.add('hidden');
            document.getElementById('setupForm').style.display = 'block';
            
            // Reset form
            document.getElementById('name').value = '';
            document.getElementById('position').value = '';
            document.getElementById('experience').value = '';
            document.getElementById('skills').value = '';
            
            // Stop camera if active
            const localVideo = document.getElementById('localVideo');
            if (localVideo.srcObject) {
                localVideo.srcObject.getTracks().forEach(track => track.stop());
                localVideo.srcObject = null;
            }
            
            addChatMessage('ai', 'Interview session ended. Thank you for your time!');
            currentQuestionIndex = 0;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Main interview page with simplified implementation"""
    return render_template_string(
        HTML_TEMPLATE,
        backend_url=BACKEND_URL
    )

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "simplified_livekit_client"}

if __name__ == '__main__':
    print("🎤 Starting Simplified LiveKit Interview Client...")
    print(f"🌐 Frontend: http://localhost:3002")
    print(f"🔗 Backend API: {BACKEND_URL}")
    print("\n✅ Features:")
    print("  - Working interview form")
    print("  - Session creation with backend")
    print("  - Camera access (if available)")
    print("  - Simulated AI interview questions")
    print("  - Interactive chat interface")
    print("  - Audio/video controls")
    
    app.run(host='0.0.0.0', port=3002, debug=True)
