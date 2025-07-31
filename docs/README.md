# Pure LiveKit Interview System

**Production-ready AI-powered interview system using LiveKit Agents framework**

## Features

- Pure LiveKit Implementation - Real-time voice communication
- Google Realtime Voice AI - Natural conversation with Gemini 2.0 Flash
- Database Persistence - SQLite storage for all interview data
- Function Tools - Professional interview management with detailed logging
- Comprehensive Evaluation - AI-powered response assessment
- Production Ready - Clean architecture and proper error handling

## Architecture

```
LiveKit Server (Docker) <-> LiveKit Agent <-> Google Realtime API
         ^                        ^                    ^
   Web Client UI           Interview Tools        AI Processing
         ^                        ^                    ^
   Candidate Audio          SQLite Database      Voice Analysis
```

## Quick Start

### 1. Environment Setup
```bash
# Copy environment template
cp config/.env.example config/.env

# Edit config/.env and add your Google API key
GOOGLE_API_KEY=your_google_api_key_here
```

### 2. Start LiveKit Server
```bash
cd docker/
docker-compose up -d
```

### 3. Start Interview Agent
```bash
python core/pure_livekit_interview_agent.py dev
```

### 4. Create Test Session
```bash
python utils/generate_web_url.py
```

### 5. Test the System
```bash
python tests/test_complete_flow.py
```

## Project Structure

```
├── core/           # Main system files
│   ├── pure_livekit_interview_agent.py  # Main agent
│   ├── interview_tools.py               # Function tools
│   └── interview_prompts.py             # AI instructions
├── config/         # Configuration files
│   ├── .env        # Environment variables
│   └── livekit.yaml # LiveKit server config
├── database/       # SQLite database
├── docker/         # LiveKit server setup
├── utils/          # Helper scripts
├── tests/          # Testing utilities
└── docs/           # Documentation
```

## Core Components

### Interview Agent
- **File**: `core/pure_livekit_interview_agent.py`
- **Purpose**: Main LiveKit agent with Google Realtime API integration
- **Features**: Voice processing, tool integration, session management

### Interview Tools
- **File**: `core/interview_tools.py`
- **Functions**: 
  - `get_candidate_profile()` - Retrieve session info
  - `generate_interview_questions()` - Create personalized questions
  - `evaluate_candidate_response()` - Assess answers
  - `save_interview_response()` - Store data
  - `complete_interview_session()` - Finalize interview

### Database Schema
- **candidate_profiles**: Session and candidate information
- **interview_responses**: Questions, answers, and evaluations
- **interview_sessions**: Overall assessments and completion data

## Interview Flow

1. **Candidate joins** LiveKit room
2. **AI detects** participant and starts interview
3. **AI calls** `get_candidate_profile()` to get session details
4. **AI generates** personalized questions using `generate_interview_questions()`
5. **Voice conversation** happens in real-time
6. **AI evaluates** each response using `evaluate_candidate_response()`
7. **Data is stored** using `save_interview_response()`
8. **Interview completes** with `complete_interview_session()`

## Development

- **Language**: Python 3.9+
- **Framework**: LiveKit Agents
- **Database**: SQLite
- **AI**: Google Gemini 2.0 Flash Realtime API
- **Voice**: LiveKit RTC

## View Interview Data

```bash
# View all interviews
python utils/view_database.py

# Query specific interviews
python utils/query_interviews.py

# Simple data viewer
python utils/simple_view_data.py
```

## Testing

```bash
# Complete system test
python tests/test_complete_flow.py

# Check database
python utils/check_database.py

# Web client test
# Open tests/test_client.html in browser
```

## LiveKit Server

The system includes Docker configuration for running a local LiveKit server:

```bash
# Start server
cd docker/
docker-compose up -d

# Check status
docker ps

# Stop server
docker-compose down
```

## Environment Variables

Required in `config/.env`:
```bash
GOOGLE_API_KEY=your_google_api_key_here
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

## Next Steps

1. **Test the system** with the provided tools
2. **Customize prompts** in `core/interview_prompts.py`
3. **Add more tools** in `core/interview_tools.py`
4. **Build frontend** using the generated URLs
5. **Deploy to production** with proper LiveKit server

## Support

- Check documentation in `docs/` folder
- Review test files in `tests/` folder
- Use utility scripts in `utils/` folder

---

**Built with LiveKit Agents and Google Realtime API**
