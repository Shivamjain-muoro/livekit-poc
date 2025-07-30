# Complete Testing Guide: LiveKit & LLM Integration

## 🎯 **What We've Built**

### ✅ **Completed Components:**
1. **Enhanced AI Backend** (`enhanced_ai_backend.py`)
   - Google Gemini AI integration for question generation
   - AI-powered answer evaluation
   - Real LiveKit token generation
   - Personalized question creation based on candidate skills

2. **Enhanced UI** (`enhanced_interview_ui.html`)
   - Real LiveKit client integration (CDN)
   - AI-powered question display
   - Enhanced feedback with AI analysis

3. **Original Working System** (`simplified_enhanced_backend.py` + `live_interview_local.html`)
   - Basic working system with predefined questions
   - Fixed validation issues

## 🚀 **Step-by-Step Testing Guide**

### **Phase 1: Test Enhanced AI Backend**

1. **Start the Enhanced Backend:**
   ```bash
   python enhanced_ai_backend.py
   ```
   
2. **Check System Health:**
   - Open: http://localhost:8002/health
   - Should show:
     ```json
     {
       "status": "healthy",
       "ai_enabled": true/false,
       "livekit_url": "ws://localhost:7880"
     }
     ```

3. **Test AI Question Generation:**
   ```bash
   curl -X POST http://localhost:8002/api/interview/create-session \
   -H "Content-Type: application/json" \
   -d '{
     "candidate": {
       "name": "Test User",
       "email": "test@example.com", 
       "position": "Software Engineer",
       "experience_level": "mid",
       "skills": ["Python", "JavaScript", "React"]
     }
   }'
   ```

### **Phase 2: Test Enhanced UI**

1. **Access Enhanced Interface:**
   - Open: http://localhost:8002/live-enhanced
   - Check AI status badge (should show "AI: Enabled" if Google API key works)

2. **Test Full Interview Flow:**
   - Fill candidate form with skills
   - Test camera/microphone
   - Start AI interview
   - Check if questions are personalized to skills entered

### **Phase 3: Test Original Working System**

1. **Access Original Interface:**
   - Open: http://localhost:8002/live-local
   - Test basic interview flow
   - Verify all validation fixes work

## 🔧 **Troubleshooting Guide**

### **Issue 1: Backend Won't Start**
```bash
# Check Python imports
python -c "import google.generativeai; print('Google AI OK')"
python -c "from livekit.api import AccessToken; print('LiveKit OK')"

# Run test script
python test_enhanced_backend.py
```

### **Issue 2: AI Not Working**
- Check `.env` file has `GOOGLE_API_KEY`
- Backend should show: "✅ Google Gemini AI initialized"
- If not, system falls back to predefined questions

### **Issue 3: LiveKit Connection Issues**
- Check LiveKit credentials in `.env`
- System works without LiveKit (fallback mode)
- For real LiveKit, need actual server running

## 📊 **Expected Results**

### **With AI Enabled:**
- Questions generated based on candidate skills
- Different questions for different positions/experience levels
- AI evaluation with detailed feedback scores
- Personalized improvement suggestions

### **Fallback Mode (No AI):**
- Predefined questions based on position type
- Basic scoring based on answer length
- Generic feedback

## 🎮 **Live Testing Scenarios**

### **Scenario 1: Senior Software Engineer**
```
Name: John Doe
Position: Senior Software Engineer
Experience: senior
Skills: Python, Docker, Kubernetes, Machine Learning, AWS
```
Expected: Advanced technical questions, ML/DevOps focus

### **Scenario 2: Entry Level Data Scientist**
```
Name: Jane Smith  
Position: Data Scientist
Experience: entry
Skills: Python, SQL, Statistics, Pandas
```
Expected: Foundational questions, basic ML concepts

### **Scenario 3: Product Manager**
```
Name: Mike Johnson
Position: Product Manager
Experience: mid
Skills: Product Strategy, Analytics, Agile, User Research
```
Expected: Behavioral/strategic questions, leadership scenarios

## 🏁 **Quick Start Commands**

```bash
# 1. Start enhanced backend
python enhanced_ai_backend.py

# 2. Test health endpoint
curl http://localhost:8002/health

# 3. Open browser
# Visit: http://localhost:8002/live-enhanced

# 4. Alternative: Original working version
# Visit: http://localhost:8002/live-local
```

## 📋 **Verification Checklist**

- [ ] Backend starts without errors
- [ ] Health endpoint returns AI status
- [ ] Enhanced UI loads with AI badges
- [ ] Original UI still works
- [ ] Session creation works
- [ ] Questions appear (AI or fallback)
- [ ] Speech recognition works
- [ ] Answer submission works
- [ ] Feedback generation works
- [ ] AI evaluation shows detailed scores (if AI enabled)

## 🔍 **Debug Information**

The system provides debug information in:
1. **Browser Console** - Frontend debug messages
2. **Backend Terminal** - Server logs and AI status
3. **Debug Panel** - Real-time frontend status
4. **Network Tab** - API request/response details

---

**Ready to test?** Start with Phase 1 and work through each step!
