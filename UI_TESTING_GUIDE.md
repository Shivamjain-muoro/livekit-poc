# 🎯 Complete Voice Interview System - UI Testing Guide

## 🚀 Quick Start Testing

### **Step 1: Start the Backend Server**

Open PowerShell in your project directory and run:

```powershell
# Option 1: Use the startup script
python start_backend.py

# Option 2: Direct command
C:/Users/ADMIN/projects/livekit-poc/venv/Scripts/python.exe realtime_voice_backend.py

# Option 3: If above fails, use the enhanced backend
C:/Users/ADMIN/projects/livekit-poc/venv/Scripts/python.exe enhanced_backend.py
```

**Expected Output:**
```
🚀 Real-Time Voice Interview Backend Starting...
🎙️ LiveKit URL: wss://livekit-poc-q1ahw2wh.livekit.cloud
🤖 LLM Integration: ✅ Enabled
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8003
```

---

## 🌐 Available UI Testing Options

### **Option 1: Voice Demo Interface (RECOMMENDED)** 🎙️
- **URL**: `http://localhost:8003/voice-demo`
- **Features**: Full voice interview with LiveKit
- **Best for**: Complete voice interaction testing

### **Option 2: Simple Interview Interface** 📝
- **URL**: `http://localhost:8002/simple` 
- **Features**: Speech-enabled without video complexity
- **Best for**: Voice testing without LiveKit dependencies

### **Option 3: Live Interview (Enhanced)** 🎥
- **URL**: `http://localhost:8002/live-fixed`
- **Features**: Video + voice with error handling
- **Best for**: Full LiveKit experience

### **Option 4: API Documentation** 📚
- **URL**: `http://localhost:8003/docs`
- **Features**: Interactive API testing
- **Best for**: Backend endpoint testing

---

## 🧪 Testing Flow - Option 1: Voice Demo Interface

### **Step 1: Open Voice Demo**
1. Start backend (see above)
2. Open browser: `http://localhost:8003/voice-demo`
3. You should see the Voice Interview Demo page

### **Step 2: Fill Candidate Information**
```
Name: John Doe
Email: john.doe@example.com  
Position: Software Engineer
Experience: Mid Level
```

### **Step 3: Create Voice Session**
1. Click **"🚀 Start Voice Interview"**
2. Wait for session creation
3. You should see: "✅ Session created! Room: interview-XXXXXXXX"

### **Step 4: Join Interview Room**
1. Click **"🎥 Join Interview Room"** 
2. Allow camera/microphone permissions when prompted
3. You should see: "🎥 Connected! The AI interviewer will start shortly..."

### **Step 5: Voice Interaction**
1. **Listen** for the AI to speak the introduction
2. **Respond** when asked questions
3. **Continue** the conversation naturally
4. **Complete** all 5 questions

---

## 🧪 Testing Flow - Option 2: Simple Interface

### **Step 1: Open Simple Interface**
1. Make sure enhanced backend is running on port 8002
2. Open: `http://localhost:8002/simple`

### **Step 2: Complete Form**
```
Full Name: Jane Smith
Email: jane.smith@example.com
Position: Frontend Developer  
Experience Level: Senior
Skills: JavaScript, React, Node.js
```

### **Step 3: Start Interview**
1. Click **"Start Interview"**
2. Watch debug log for session creation
3. Look for "Session created successfully"

### **Step 4: Voice Interaction**
1. Click **"🔊 Speak Question"** to hear AI
2. Click **"🎤 Start Recording"** to record answer
3. Speak your response clearly
4. Click **"⏹️ Stop Recording"** 
5. Review transcribed text
6. Click **"Submit Answer"**
7. Repeat for all questions

---

## 🔍 What to Test

### **🎤 Voice Features**
- [ ] **TTS (Text-to-Speech)**: AI speaks questions clearly
- [ ] **STT (Speech-to-Text)**: Your speech is transcribed accurately  
- [ ] **Microphone Detection**: System finds your microphone
- [ ] **Audio Quality**: Clear audio input/output
- [ ] **Real-time Response**: < 3 second response time

### **🤖 AI Intelligence** 
- [ ] **Question Generation**: Relevant questions for the role
- [ ] **Dynamic Evaluation**: AI provides meaningful feedback
- [ ] **Conversation Flow**: Natural progression between questions
- [ ] **Context Awareness**: AI remembers previous responses

### **💻 UI/UX Testing**
- [ ] **Session Creation**: Forms work and validate properly
- [ ] **Real-time Updates**: Progress tracking works
- [ ] **Error Handling**: Graceful error messages
- [ ] **Responsive Design**: Works on different screen sizes
- [ ] **Browser Compatibility**: Test in Chrome, Edge, Firefox

### **🎥 LiveKit Integration**
- [ ] **Room Creation**: LiveKit rooms are created successfully
- [ ] **Video/Audio**: Camera and microphone work
- [ ] **Connection Stability**: No frequent disconnections
- [ ] **Token Generation**: Access tokens work properly

---

## 🐛 Common Issues & Solutions

### **Backend Issues**
| Problem | Solution |
|---------|----------|
| Port 8003 in use | Kill process: `netstat -ano \| findstr :8003` then `taskkill /PID XXXX` |
| ImportError | Run: `pip install -r requirements.txt` |
| Database errors | Delete `interview_sessions.db` and restart |
| LiveKit errors | Check `.env` file for correct credentials |

### **Voice Issues**
| Problem | Solution |
|---------|----------|
| No microphone detected | Check browser permissions |
| TTS not working | Install: `pip install pyttsx3` |
| STT errors | Install: `pip install SpeechRecognition pyaudio` |
| Audio quality poor | Check microphone settings |

### **Browser Issues**
| Problem | Solution |
|---------|----------|
| LiveKit not loading | Refresh page, check console for errors |
| Microphone permission denied | Enable in browser settings |
| Video not showing | Check camera permissions |
| CORS errors | Ensure backend CORS is configured |

---

## 📊 Success Criteria

### **✅ Minimum Viable Test**
1. Backend starts without errors
2. UI loads and forms work
3. Session creates successfully
4. At least one question is asked and answered
5. Basic feedback is provided

### **✅ Complete Voice Test**
1. All 5 questions are completed
2. Voice input/output works clearly
3. Real-time transcription is accurate
4. AI provides meaningful feedback
5. Interview summary is generated

### **✅ Production Ready Test**
1. Multiple concurrent sessions work
2. Error handling is robust
3. Performance is acceptable (< 3s response)
4. All browser permissions work
5. LiveKit integration is stable

---

## 🎯 Sample Test Scenarios

### **Scenario 1: Technical Interview**
```
Position: Full Stack Developer
Experience: Mid Level
Expected Questions: 
- Explain REST vs GraphQL
- Database optimization strategies  
- Frontend framework preferences
- Code review best practices
- Debugging techniques
```

### **Scenario 2: Behavioral Interview**
```
Position: Team Lead
Experience: Senior Level  
Expected Questions:
- Leadership challenges
- Conflict resolution
- Team motivation strategies
- Project management approach
- Mentoring experience
```

### **Scenario 3: Entry Level Interview**
```
Position: Junior Developer
Experience: Entry Level
Expected Questions:
- Programming fundamentals
- Learning methodology
- Problem-solving approach
- Collaboration skills
- Career goals
```

---

## 📱 Browser Testing Checklist

### **Chrome (Recommended)**
- [ ] Voice permissions work
- [ ] LiveKit loads properly
- [ ] Audio/video quality good
- [ ] Console shows no errors

### **Edge**
- [ ] All features work
- [ ] Performance acceptable
- [ ] Voice recognition accurate

### **Firefox**
- [ ] Basic functionality works
- [ ] May have LiveKit limitations
- [ ] Voice features may vary

---

## 🔧 Advanced Testing

### **API Testing**
Use the API docs at `http://localhost:8003/docs` to test:

1. **Create Session**: `POST /api/voice-interview/create`
2. **Start Interview**: `POST /api/interview/start/{session_id}`
3. **Submit Answer**: `POST /api/interview/{session_id}/answer`
4. **Get Summary**: `GET /api/interview/summary/{session_id}`

### **WebSocket Testing**
Connect to: `ws://localhost:8003/ws/interview/{session_id}`
- Test real-time updates
- Monitor interview progress
- Check connection stability

### **Performance Testing**
- Monitor CPU/Memory usage during interviews
- Test with multiple concurrent sessions
- Measure response times
- Check for memory leaks

---

## 🎉 Ready to Test!

1. **Start Backend**: `python start_backend.py`
2. **Open Browser**: `http://localhost:8003/voice-demo`
3. **Create Session**: Fill form and start interview
4. **Test Voice**: Speak with the AI interviewer
5. **Verify Results**: Check interview summary

**Your voice interview system is ready for comprehensive testing!** 🚀

---

*For issues or questions, check the console logs and error messages for detailed debugging information.*
