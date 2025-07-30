"""
Minimal test for session creation without LLM dependencies
"""
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add current directory to path
sys.path.append(os.getcwd())

# Import models
from models.interview_models import (
    Candidate, SessionCreateRequest, SessionResponse, 
    ExperienceLevel
)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Minimal backend is running"}

@app.post("/api/interview/create-session")
async def create_interview_session(request: SessionCreateRequest):
    """Create a simple session without LLM dependencies"""
    try:
        # Simple session creation
        session_id = f"session_{os.urandom(8).hex()}"
        room_name = f"room_{session_id}"
        
        # Return minimal response
        return SessionResponse(
            session_id=session_id,
            room_name=room_name,
            participant_token="dummy_participant_token",
            agent_token="dummy_agent_token",
            livekit_url="ws://localhost:7880",
            status="created"
        )
    except Exception as e:
        print(f"Error creating session: {e}")
        raise

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting minimal backend on http://localhost:8003")
    uvicorn.run(app, host="0.0.0.0", port=8003)
