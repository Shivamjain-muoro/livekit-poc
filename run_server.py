#!/usr/bin/env python3
"""
Server Starter Script
"""
import subprocess
import sys
import os

def start_server():
    """Start the enhanced backend server"""
    try:
        # Change to the correct directory
        os.chdir(r"c:\Users\ADMIN\projects\livekit-poc")
        
        # Start the server
        print("🚀 Starting Enhanced Backend Server...")
        print("📍 Directory:", os.getcwd())
        print("🌐 Server will be available at: http://localhost:8002")
        print("=" * 50)
        
        # Import and run directly
        import uvicorn
        
        # Start without reload for stability
        uvicorn.run(
            "enhanced_backend:app",
            host="0.0.0.0",
            port=8002,
            reload=False,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
