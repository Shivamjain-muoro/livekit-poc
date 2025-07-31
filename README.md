# LiveKit Interview System

A professional AI-powered interview platform using LiveKit for real-time voice conversations, Google's Gemini AI for intelligent responses, and comprehensive data storage for interview analytics.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Docker and Docker Compose
- Google AI API key

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd livekit-poc
```

### 2. Environment Configuration
Copy the environment template and add your API keys:
```bash
cp config/.env.example config/.env
```

Edit `config/.env` and add your Google AI API key:
```
GOOGLE_API_KEY=your_google_ai_api_key_here
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

### 3. Install Dependencies
```bash
pip install -r config/requirements.txt
```

### 4. Start the LiveKit Server
```bash
cd docker
docker-compose up -d
```

Verify the server is running:
```bash
docker ps
```

You should see both `livekit-server` and `livekit-redis` containers running.

### 5. Start the Interview Agent
```bash
# From the project root
python core/pure_livekit_interview_agent.py dev
```

### 6. Create an Interview Session
In a new terminal:
```bash
python utils/generate_web_url.py
```

This will generate a web URL that candidates can use to join the interview.

## 📊 Database Management

### View All Interview Data
```bash
python utils/view_database.py
```

### Check Database Status
```bash
python utils/check_database.py
```

### Query Specific Interviews
```bash
python utils/query_interviews.py
```

### Simple Data Viewer
```bash
python utils/simple_view_data.py
```

## 🗂️ Project Structure

```
livekit-interview-system/
├── 📂 core/                    # Main system files
│   ├── pure_livekit_interview_agent.py    # Main LiveKit agent
│   ├── interview_tools.py                 # Function tools with database
│   └── interview_prompts.py               # AI instructions and prompts
├── 📂 config/                  # Configuration
│   ├── .env                              # Environment variables
│   ├── .env.example                      # Environment template
│   ├── requirements.txt                  # Python dependencies
│   └── livekit.yaml                      # LiveKit server config
├── 📂 database/                # Data storage
│   └── interview_sessions.db             # SQLite database
├── 📂 docker/                  # LiveKit server setup
│   ├── docker-compose.yml               # Main Docker config
│   └── docker-compose-simple.yml        # Alternative config
├── 📂 utils/                   # Helper scripts
│   ├── generate_web_url.py               # URL/token generator
│   ├── view_database.py                  # Database viewer
│   ├── simple_view_data.py               # Simple data viewer
│   ├── query_interviews.py               # Interview queries
│   └── check_database.py                 # Database checker
├── 📂 tests/                   # Testing
│   ├── test_complete_flow.py             # Complete system test
│   └── test_client.html                  # Web test client
└── 📂 docs/                    # Documentation
```

## 🛠️ Troubleshooting

### LiveKit Server Issues

**Check server status:**
```bash
cd docker
docker ps
docker logs livekit-server --tail 20
```

**Restart the server:**
```bash
docker-compose restart
```

**Server won't start:**
1. Check if ports 7880-7882 are available
2. Verify Docker is running
3. Check the configuration in `docker-compose.yml`

### Database Issues

**Database not found:**
- The database is created automatically when first accessed
- Ensure the `database/` folder exists
- Check file permissions

**View database tables:**
```bash
sqlite3 database/interview_sessions.db ".tables"
```

### Agent Connection Issues

**Agent won't connect:**
1. Ensure LiveKit server is running (`docker ps`)
2. Check environment variables in `config/.env`
3. Verify Google API key is valid
4. Check network connectivity

### Environment Issues

**Missing dependencies:**
```bash
pip install -r config/requirements.txt
```

**Python path issues:**
Make sure you're running from the project root directory.

## 🎯 Usage Workflows

### Starting a Complete Interview Session

1. **Start the infrastructure:**
   ```bash
   cd docker && docker-compose up -d
   ```

2. **Start the agent:**
   ```bash
   python core/pure_livekit_interview_agent.py dev
   ```

3. **Generate candidate URL:**
   ```bash
   python utils/generate_web_url.py
   ```

4. **Send URL to candidate** - they can join via browser

5. **Monitor the interview** via agent logs

6. **Check results:**
   ```bash
   python utils/view_database.py
   ```

### Viewing Interview Results

After interviews are completed, you can view the data in several ways:

**Complete database view:**
```bash
python utils/view_database.py
```

**Quick data summary:**
```bash
python utils/simple_view_data.py
```

**Interactive queries:**
```bash
python utils/query_interviews.py
```

## 🗄️ Database Schema

The system uses SQLite with the following main tables:

- **candidate_profiles** - Candidate information and session details
- **interview_responses** - Questions, answers, and evaluations
- **interview_sessions** - Session metadata and final assessments

## 🔧 Configuration

### LiveKit Server Configuration
The server configuration is in `docker/docker-compose.yml` and uses environment variables for:
- API keys and secrets
- Redis connection
- Development mode settings
- Port configurations

### Agent Configuration
The agent configuration is in `core/pure_livekit_interview_agent.py` and includes:
- Google AI model settings
- Voice configuration
- Tool integrations
- Error handling

## 🧪 Testing

**Run complete system test:**
```bash
python tests/test_complete_flow.py
```

**Test web client:**
Open `tests/test_client.html` in a browser after generating a token.

## 📝 Development

### Adding New Interview Questions
Edit `core/interview_tools.py` in the `generate_interview_questions` function.

### Modifying AI Behavior
Edit the prompts in `core/interview_prompts.py`.

### Adding Database Fields
Modify the schema in `core/interview_tools.py` in the database initialization functions.

## 🚦 System Status Commands

**Check everything is working:**
```bash
# 1. Check Docker containers
docker ps

# 2. Check database
python utils/check_database.py

# 3. Test token generation
python utils/generate_web_url.py

# 4. View existing data
python utils/view_database.py
```

## 🎉 Success Indicators

Your system is working correctly when:
- ✅ Docker containers are running (livekit-server and livekit-redis)
- ✅ Agent connects without errors
- ✅ Token generation works
- ✅ Database queries return data
- ✅ Web client can connect to the generated URL

## 📞 Support

For issues:
1. Check the troubleshooting section above
2. Review Docker and agent logs
3. Verify environment configuration
4. Test each component individually

## 🔐 Security Notes

- Keep your `.env` file secure and never commit it to version control
- Use strong API keys in production
- Consider implementing authentication for production deployments
- The current setup is designed for development/testing environments
