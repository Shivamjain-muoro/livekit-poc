# 🏠 Local AI Interview System - Setup & Demo Guide

## 📋 Prerequisites

### Required Software:
- ✅ **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop)
- ✅ **Python 3.8+** - Already installed
- ✅ **Git** - Already installed

### System Requirements:
- 🖥️ **OS:** Windows 10/11
- 💾 **RAM:** 4GB minimum (8GB recommended)
- 🌐 **Network:** Internet for initial Docker image download

## 🚀 Quick Start (For Manager Demo)

### Option 1: One-Click Startup
```bash
# Double-click this file to start everything:
start_local_system.bat
```

### Option 2: Step-by-Step
```bash
# 1. Check system status
python check_local_status.py

# 2. Start LiveKit server
docker-compose up livekit

# 3. Start AI agent
python complete_interview_agent.py

# 4. Start web interface  
cd web && python -m http.server 8080

# 5. Open browser
http://localhost:8080
```

## 📊 System Components

### 🏗️ Architecture Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   LiveKit       │    │   AI Agent     │
│   (Frontend)    │◄──►│   Server        │◄──►│   (Backend)     │
│   Port 8080     │    │   Port 7880     │    │   Local Process │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────┐
                    │   Database      │
                    │   SQLite Local  │
                    └─────────────────┘
```

### 🔧 Configuration Files
- **Environment:** `config/.env` - Contains API keys and settings
- **LiveKit:** `config/livekit.yaml` - Server configuration
- **Docker:** `docker-compose.yml` - Container orchestration

## 🎯 Demo Flow for Manager

### 1. System Startup (2 minutes)
```bash
# Start everything with one command
.\start_local_system.bat

# Expected output:
# ✅ LiveKit server started
# ✅ AI agent running  
# ✅ Web server active
# ✅ Browser opens automatically
```

### 2. Create Interview Session (1 minute)
1. Open: `http://localhost:8080`
2. Fill candidate details
3. Click "Generate Interview Session"
4. Copy the meeting URL

### 3. Conduct Interview (5 minutes)
1. Open meeting URL in browser
2. Allow microphone access
3. AI starts interview automatically
4. Answer 2-3 questions normally
5. End interview

### 4. View Results (1 minute)
1. Click "View Results" button
2. See automatic evaluation scores
3. Review conversation transcript
4. Check database entries

### 5. System Shutdown (30 seconds)
```bash
# Stop everything cleanly
.\stop_local_system.bat
```

## 📈 What Manager Will See

### ✅ Complete Local Solution
- **No cloud dependencies** - Everything runs locally
- **Real-time AI interviews** - Voice conversation with AI
- **Automatic evaluation** - Scoring without manual intervention
- **Professional interface** - Clean, branded web portal
- **Secure & private** - All data stays on local machine

### 📊 Technical Capabilities
- **Real-time voice processing** - Google Gemini Realtime API
- **Automated scoring** - AI evaluates responses instantly
- **Comprehensive database** - SQLite with full evaluation data
- **Modern web interface** - Responsive, professional design
- **Easy deployment** - One-command startup and shutdown

## 🔍 Verification Commands

### System Health Check
```bash
python check_local_status.py
```

### Generate Demo Session
```bash
python local_token_generator.py
```

### View Database
```bash
python check_interview_results.py
```

### Check Logs
```bash
docker logs livekit-local
```

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### ❌ "Docker not found"
```bash
# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop
```

#### ❌ "Port 7880 already in use" 
```bash
# Stop existing LiveKit containers
docker stop $(docker ps -q --filter ancestor=livekit/livekit-server)
```

#### ❌ "Web server won't start"
```bash
# Check if port 8080 is free
netstat -an | findstr :8080

# Use different port if needed
python -m http.server 8081
```

#### ❌ "AI agent connection failed"
```bash
# Verify environment variables
type config\.env

# Check LiveKit server status  
docker ps | findstr livekit
```

## 🎯 Manager Presentation Points

### 🏆 Benefits Demonstrated
1. **Complete Control** - No external dependencies
2. **Cost Effective** - No cloud hosting fees
3. **Data Security** - Everything stays internal
4. **Easy Scaling** - Can deploy on any machine
5. **Customizable** - Full control over features and branding

### 📊 Technical Highlights
1. **Modern Stack** - Docker, Python, WebRTC, AI
2. **Production Ready** - Proper error handling and logging
3. **Maintainable** - Clear architecture and documentation  
4. **Extensible** - Easy to add new features
5. **Reliable** - Automated systems with fallbacks

### 💼 Business Value
1. **Reduces HR workload** - Automated initial screening
2. **Consistent evaluation** - AI removes human bias
3. **Scalable interviews** - Handle multiple candidates
4. **Detailed reporting** - Comprehensive candidate analysis
5. **Cost savings** - No per-interview charges

## 📞 Support

If you encounter any issues during the demo:
1. Run: `python check_local_status.py`
2. Check: `docker logs livekit-local`
3. Restart: `.\stop_local_system.bat` then `.\start_local_system.bat`

---

## 🎉 Ready for Demo!

The system is now fully configured for local demonstration. Everything runs on `localhost` with no external dependencies.
