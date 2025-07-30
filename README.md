# 🤖 AI Interview System

A comprehensive AI-powered interview platform built with Python, FastAPI, LiveKit, and LLM integration. This system provides a complete backend solution for conducting automated interviews with real-time evaluation and feedback.

## 🚀 Features

### Core Functionality
- **AI-Powered Interviews**: Automated question generation and evaluation
- **Real-time Audio/Video**: LiveKit integration for live interviews  
- **Smart Evaluation**: LLM-based answer scoring and feedback
- **Progress Tracking**: Complete interview flow management
- **Comprehensive Reporting**: Detailed candidate assessments

### Technical Stack
- **Backend**: FastAPI with async support
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **AI Integration**: OpenAI GPT-4 with Google Gemini fallback
- **Real-time**: LiveKit for audio/video communication
- **Frontend**: Responsive HTML/CSS/JavaScript demo

## 🎯 Quick Start

### 1. Start the Backend
```bash
cd livekit-poc
python enhanced_backend.py
```

### 2. Access the Demo
- **Demo Interface**: http://localhost:8002
- **API Documentation**: http://localhost:8002/docs
- **Health Check**: http://localhost:8002/health

### 3. Test Complete Flow
1. Open the demo at http://localhost:8002
2. Fill in candidate information
3. Create and start interview session
4. Answer questions and receive AI feedback
5. View comprehensive interview summary
- **Comprehensive Evaluation & Scoring**
- **Interview Dashboard & Analytics**

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Create a `.env` file with your credentials:
```env
# Google Cloud credentials for speech/LLM
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account.json

# Optional: Email notifications
GMAIL_USER=your.email@gmail.com
GMAIL_APP_PASSWORD=your_app_password

# LiveKit credentials (if using hosted service)
LIVEKIT_URL=wss://your-livekit-url.com
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
```

### 3. Run Demo
```bash
python demo.py
```

## 🎬 Demo Flow

### For Your Manager Demo:

1. **Start the Interview Agent**
   ```bash
   python agent.py
   ```

2. **Start Web Dashboard** (in another terminal)
   ```bash
   python dashboard.py
   ```
   Then open http://localhost:8000

3. **Demo Interview Flow:**
   - "Hi, I want to start an interview"
   - "My name is Alice Johnson, email alice@example.com, applying for software_engineer, mid level"
   - Upload resume text
   - Answer generated questions
   - Get evaluation and feedback

## 📊 Key Features Demo

### 1. Interview Session Management
- Create sessions with candidate details
- Track interview progress and status
- Handle pause/resume functionality

### 2. Smart Resume Analysis
- Extract skills and experience automatically
- Match candidates to job requirements
- Generate role-specific questions

### 3. Adaptive Question Generation
- Technical questions based on job role
- Behavioral questions for soft skills
- Difficulty adjustment by experience level

### 4. Real-time Interview Conduct
- Timed questions with response tracking
- Professional interview flow
- Comprehensive answer recording

### 5. Advanced Evaluation System
- Multi-criteria scoring (technical, communication, etc.)
- Weighted evaluation based on role requirements
- Detailed feedback generation

### 6. Analytics Dashboard
- Session overview and statistics
- Detailed interview reports
- Candidate performance tracking

## 🎯 Key MVP Features

✅ **Complete Interview Flow**
✅ **Resume Analysis**
✅ **Question Generation** 
✅ **Answer Evaluation**
✅ **Score Calculation**
✅ **Web Dashboard**
✅ **Session Management**
✅ **Data Persistence**

## 🔧 Architecture

```
AI Interview Agent
├── agent.py          # Main LiveKit agent
├── tools.py          # Interview functions
├── prompts.py        # AI instructions
├── models.py         # Data structures
├── config.py         # Settings
├── database.py       # Data storage
├── dashboard.py      # Web interface
└── demo.py           # Demo script
```

## 📈 Scalability Features

- **Database Integration**: Easy to switch to PostgreSQL/MongoDB
- **API Ready**: RESTful endpoints for integration
- **Modular Design**: Easy to add new features
- **Cloud Deploy Ready**: Works with Docker/Kubernetes

## 🎪 Demo Script for Manager

"I'll demonstrate our AI Interview Agent MVP that rivals Mercor AI's functionality:

1. **Session Creation**: Creates structured interview sessions
2. **Resume Processing**: Analyzes and extracts candidate skills
3. **Smart Questions**: Generates role-specific questions automatically
4. **Live Interview**: Conducts professional interviews with timing
5. **Evaluation**: Provides comprehensive scoring and feedback
6. **Dashboard**: Shows all interviews and analytics

This MVP includes all core features needed for automated technical interviews and can be extended with video analysis, advanced AI evaluation, and more."

## 📞 Next Steps for Production

1. **Enhanced AI Evaluation** with GPT-4/Claude
2. **Video Analysis** for behavior detection
3. **Advanced Question Pool** with 1000+ questions
4. **Integration APIs** for ATS systems
5. **Mobile App** for candidates
6. **Advanced Analytics** and ML insights

Ready to impress your manager! 🚀
